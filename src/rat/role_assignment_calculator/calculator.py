from copy import deepcopy

from pysat.examples.fm import FM
from pysat.examples.rc2 import RC2, RC2Stratified
from pysat.formula import IDPool, WCNFPlus, CNFPlus
from pysat.solvers import Solver

from rat.io import (
    Role,
    Student,
    RoleCouplingGraph,
    RoleGender,
    STUDENT_TO_ROLE_GENDER_MAP,
    StudentGender,
)

ESSENTIALS_GENDER_MATCHING_WEIGHT = 100000
PRIORITY_ROLES_WEIGHT = 1000
GENDER_PREFERENCE_WEIGHT = 1


class Calculator:
    def __init__(
        self,
        roles: set[Role],
        students: set[Student],
        role_couplings: RoleCouplingGraph = None,
        essential_roles: set[Role] = None,
        priority_roles: set[Role] = None,
        blacklisted_roles: set[Role] = None,
    ):
        self.roles = roles
        self.essential_roles = essential_roles
        self.priority_roles = priority_roles
        self.blacklisted_roles = blacklisted_roles
        self.students = students
        self.variable_pool = IDPool()
        self._fill_variable_pool(roles, students)

        self._roles_with_gender = {
            RoleGender.NON_BINARY: set(
                [role for role in self.roles if role.gender == RoleGender.NON_BINARY]
            ),
            RoleGender.NEUTRAL: set(
                [role for role in self.roles if role.gender == RoleGender.NEUTRAL]
            ),
            RoleGender.MALE: set(
                [role for role in self.roles if role.gender == RoleGender.MALE]
            ),
            RoleGender.FEMALE: set(
                [role for role in self.roles if role.gender == RoleGender.FEMALE]
            ),
        }

        self._students_with_gender = {
            StudentGender.NON_BINARY: set(
                [s for s in self.students if s.gender == StudentGender.NON_BINARY]
            ),
            StudentGender.MALE: set(
                [s for s in self.students if s.gender == StudentGender.MALE]
            ),
            StudentGender.FEMALE: set(
                [s for s in self.students if s.gender == StudentGender.FEMALE]
            ),
        }

        self._essential_roles_with_gender = None
        if essential_roles is not None:
            self._essential_roles_with_gender = {
                RoleGender.NON_BINARY: set(
                    [
                        role
                        for role in self.essential_roles
                        if role.gender == RoleGender.NON_BINARY
                    ]
                ),
                RoleGender.NEUTRAL: set(
                    [
                        role
                        for role in self.essential_roles
                        if role.gender == RoleGender.NEUTRAL
                    ]
                ),
                RoleGender.MALE: set(
                    [
                        role
                        for role in self.essential_roles
                        if role.gender == RoleGender.MALE
                    ]
                ),
                RoleGender.FEMALE: set(
                    [
                        role
                        for role in self.essential_roles
                        if role.gender == RoleGender.FEMALE
                    ]
                ),
            }

    def calculate_role_assignments(self) -> dict[Student, Role]:
        if self._trivially_unsatisfiable():
            print("Role assignment could not be found: trivially unsatisfiable")
            return {}

        formula = CNFPlus()
        self._every_student_has_exactly_one_role(formula)
        self._students_have_pairwise_different_roles(formula)
        self._enforce_gender_vetoes(formula)
        if self.blacklisted_roles is not None:
            self._blacklist_roles(formula)
        if self.essential_roles is not None:
            self._enforce_essential_roles(formula)

        with Solver(name="gluecard4", bootstrap_with=formula) as solver:
            if solver.solve():
                print("Role Assignment Found")
                return self._interpret_model(solver.get_model())
            else:
                print("Role Assignment Could Not Be Found")
                return {}

    def _trivially_unsatisfiable(self):
        if len(self.students) > len(self.roles):
            return True
        if self.essential_roles is not None:
            if len(self.essential_roles) > len(self.students):
                return True
            if not self._enough_students_to_play_essential_roles_with_gender(
                RoleGender.MALE
            ):
                return True
            if not self._enough_students_to_play_essential_roles_with_gender(
                RoleGender.FEMALE
            ):
                return True
            if not self._enough_students_to_play_essential_roles_with_gender(
                RoleGender.NON_BINARY
            ):
                return True
        return False

    def _enough_students_to_play_essential_roles_with_gender(
        self, role_gender: RoleGender
    ):
        return self._get_essential_roles_with_gender(
            role_gender
        ) <= self._students_willing_to_play_role_with_gender(role_gender)

    def _get_essential_roles_with_gender(self, role_gender):
        return len([r for r in self.essential_roles if r.gender == role_gender])

    def _students_willing_to_play_role_with_gender(self, role_gender):
        return len(
            [s for s in self.students if role_gender not in s.get_vetoed_genders()]
        )

    def _fill_variable_pool(self, roles: set[Role], students: set[Student]):
        for s in students:
            for r in roles:
                self.variable_pool.id((s, r))

    def _student_has_role(self, s: Student, r: Role):
        if not isinstance(s, Student):
            raise TypeError(f"{s} is expected to be a Student!")
        if not isinstance(r, Role):
            raise TypeError(f"{r} is expected to be a Role!")
        return self.variable_pool.id((s, r))

    def _every_student_has_exactly_one_role(self, formula: WCNFPlus):
        """
        Extends the formula with clauses, which state that
        every student must have exactly one role.

        Args:
            formula: the formula to extend.
        """
        for student in self.students:
            at_mosts = []
            at_leasts = []
            for role in self.roles:
                at_mosts.append(self._student_has_role(student, role))
                at_leasts.append(-1 * self._student_has_role(student, role))
            formula.append([at_mosts, 1], is_atmost=True)
            formula.append([at_leasts, len(self.roles) - 1], is_atmost=True)

    def _every_student_has_at_least_one_role(self, formula: WCNFPlus):
        pass

    def _every_student_has_at_most_one_role(self, formula: WCNFPlus):
        pass

    def _students_have_pairwise_different_roles(self, formula: WCNFPlus):
        """
        Extends the formula with clauses, which state that
        the roles of students must be pairwise different.

        Args:
            formula: the formula to extend
        """
        for this_role in self.roles:
            relevant_variables = []
            for this_student in self.students:
                relevant_variables.append(
                    self._student_has_role(this_student, this_role)
                )
            formula.append([relevant_variables, 1], is_atmost=True)

    def _enforce_gender_vetoes(self, formula: WCNFPlus):
        """
        Gets gender vetoes as a list of negative literals, intended as a list of assumptions.
        """
        ban_list = [
            self._student_has_role(student, vetoed_role)
            for student in self.students
            for vetoed_gender in student.get_vetoed_genders()
            for vetoed_role in self._roles_with_gender.get(vetoed_gender)
        ]
        formula.append([ban_list, 0], is_atmost=True)

    def _set_role_couplings(self, formula: WCNFPlus, role_couplings: RoleCouplingGraph):
        """
        Extends the CNF formula with clauses, which state that given roles are coupled to one another other.
        """
        for role in role_couplings.map.keys():
            for coupled_role in role_couplings.map[role]:
                self._couple_roles(formula, role, coupled_role)

    def _couple_roles(self, formula: WCNFPlus, role: Role, coupled_role: Role):
        """
        Extends the CNF formula with clauses, which couple the roles.
        """
        # role is not occupied by this_student or coupled_role is occupied by at least one student
        for this_student in self.students:
            relevant_variables = []
            for other_student in self.students:
                relevant_variables.append(
                    self._student_has_role(other_student, coupled_role)
                )
            formula.append(
                [-1 * self._student_has_role(this_student, role)] + relevant_variables
            )

    def _enforce_essential_roles(self, formula: WCNFPlus):
        for role in self.essential_roles:
            at_leasts = []
            for student in self.students:
                at_leasts.append(-1 * self._student_has_role(student, role))
            formula.append([at_leasts, len(self.students) - 1], is_atmost=True)

    def _gender_matching_for_essential_roles(self, formula: WCNFPlus):
        """
        Coerces the formula to match essential roles to students of the matching gender.

        Each essential role should at least have a student of the matching gender playing it.
        """
        for student_gender, matching_students in self._students_with_gender.items():
            preferred_role_gender = STUDENT_TO_ROLE_GENDER_MAP.get(student_gender)
            matching_roles = self._essential_roles_with_gender.get(
                preferred_role_gender
            ).union(self._essential_roles_with_gender.get(RoleGender.NEUTRAL))
            for preferred_role in matching_roles:
                formula.append(
                    [
                        self._student_has_role(s, preferred_role)
                        for s in matching_students
                    ],
                    weight=ESSENTIALS_GENDER_MATCHING_WEIGHT,
                )

    def _highlight_priority_roles(self, formula: WCNFPlus):
        for role in self.priority_roles:
            role_is_occupied_clause = []
            for student in self.students:
                role_is_occupied_clause.append(self._student_has_role(student, role))
            formula.append(role_is_occupied_clause, weight=PRIORITY_ROLES_WEIGHT)

    def _blacklist_roles(self, formula: WCNFPlus):
        for role in self.blacklisted_roles:
            for student in self.students:
                formula.append([-1 * self._student_has_role(student, role)])

    def _interpret_model(self, model) -> dict[Student, Role]:
        role_assignments = []
        for variable in model:
            if variable > 0:
                role_assignments.append(self.variable_pool.obj(variable))

        output = {}
        for ra in role_assignments:
            # The variable pool has a mapping of integer IDs to the tuple defined in _student_has_role(s, r)
            student = ra[0]
            role = ra[1]
            output[student] = role
        return output

    def _get_roles_with_gender(self, vetoed_gender: RoleGender):
        output = []
        for role in self.roles:
            if role.gender == vetoed_gender:
                output.append(role)
        return set(output)
