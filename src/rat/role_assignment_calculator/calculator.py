from copy import deepcopy
from threading import Timer
from typing import Tuple

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

CONFLICT_BUDGET = 10_000


def _gender_matches(assignment: Tuple[Student, Role]) -> bool:
    return (
        assignment[1].gender == RoleGender.NEUTRAL
        or STUDENT_TO_ROLE_GENDER_MAP.get(assignment[0].gender) == assignment[1].gender
    )


def _call_sat_solver(formula: CNFPlus) -> None | list[int]:
    with Solver(name="gluecard4", bootstrap_with=formula) as solver:
        solver.conf_budget(CONFLICT_BUDGET)
        sat = solver.solve_limited()
        if sat is None:
            return None
        else:
            return solver.get_model() if sat is True else None


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

    def _student_has_role(self, s: Student, r: Role) -> int:
        if not isinstance(s, Student):
            raise TypeError(f"{s} is expected to be a Student!")
        if not isinstance(r, Role):
            raise TypeError(f"{r} is expected to be a Role!")
        return self.variable_pool.id((s, r))

    def _gender_match(self, s: Student) -> int:
        return self.variable_pool.id(s)

    def calculate_role_assignments(self) -> dict[Student, Role]:
        if self._trivially_unsatisfiable():
            print("Role assignment could not be found: trivially unsatisfiable")
            return {}

        last_optimal_assignment = _call_sat_solver(
            self._build_formula_without_gender_matching()
        )
        if last_optimal_assignment is None:
            print("Role assignment could not be found")
            return {}

        high = len(self.students)
        low = 0
        # Use binary search to look for the optimal number of students to gender match.
        while low <= high:
            mid = low + (high - low) // 2
            formula = self._build_formula_without_gender_matching()
            self._enforce_gender_matching_for_n_students(formula, mid)
            candidate_assignment = _call_sat_solver(formula)

            if candidate_assignment is not None:
                low = mid + 1
                last_optimal_assignment = candidate_assignment
            else:
                high = mid - 1

        return self._interpret_model(last_optimal_assignment)

    def _build_formula_without_gender_matching(self):
        formula = CNFPlus()
        self._every_student_has_exactly_one_role(formula)
        self._students_have_pairwise_different_roles(formula)
        self._enforce_gender_vetoes(formula)
        if self.blacklisted_roles is not None:
            self._blacklist_roles(formula)
        if self.essential_roles is not None:
            self._enforce_essential_roles(formula)
        return formula

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

    def _every_student_has_exactly_one_role(self, formula: CNFPlus):
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

    def _students_have_pairwise_different_roles(self, formula: CNFPlus):
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

    def _enforce_gender_vetoes(self, formula: CNFPlus):
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

    def _set_role_couplings(self, formula: CNFPlus, role_couplings: RoleCouplingGraph):
        """
        Extends the CNF formula with clauses, which state that given roles are coupled to one another other.
        """
        for role in role_couplings.map.keys():
            for coupled_role in role_couplings.map[role]:
                self._couple_roles(formula, role, coupled_role)

    def _couple_roles(self, formula: CNFPlus, role: Role, coupled_role: Role):
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

    def _enforce_essential_roles(self, formula: CNFPlus):
        for role in self.essential_roles:
            at_leasts = []
            for student in self.students:
                at_leasts.append(-1 * self._student_has_role(student, role))
            formula.append([at_leasts, len(self.students) - 1], is_atmost=True)

    def _blacklist_roles(self, formula: CNFPlus):
        for role in self.blacklisted_roles:
            for student in self.students:
                formula.append([-1 * self._student_has_role(student, role)])

    def _enforce_gender_matching_for_n_students(
        self, formula: CNFPlus, number_of_students_to_match: int
    ):
        """
        Extends the CNF formula with clauses, which state that at least a given amount of students
        must have a role that matches their gender.
        """
        if number_of_students_to_match == 0:
            return
        gender_match_literals = []
        for s in self.students:
            # s is gender-matched --> s is assigned at least one role that matches their gender
            gender_match_literal = -1 * self._gender_match(s)
            gender_match_literals.append(gender_match_literal)
            formula.append(
                [gender_match_literal]
                + [
                    self._student_has_role(s, matching_role)
                    for matching_role in self._get_matching_roles_for_student(s)
                ]
            )
        formula.append(
            [gender_match_literals, len(self.students) - number_of_students_to_match],
            is_atmost=True,
        )

    def _get_matching_roles_for_student(self, student: Student):
        """
        Get all roles that match the student's gender. Neutral roles inclusive.
        """
        return self._roles_with_gender.get(
            STUDENT_TO_ROLE_GENDER_MAP.get(student.gender)
        ).union(self._roles_with_gender.get(RoleGender.NEUTRAL))

    def _interpret_model(self, model) -> dict[Student, Role]:
        role_assignments = []
        for variable in model:
            if variable > 0:
                role_assignments.append(self.variable_pool.obj(variable))

        output = {}
        for ra in role_assignments:
            # The variable pool has a mapping of integer IDs to the tuple defined in _student_has_role(s, r)
            if isinstance(ra, tuple):
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
