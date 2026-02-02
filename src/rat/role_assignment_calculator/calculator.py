from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNFPlus

from rat.io import (
    Role,
    Student,
    RoleCouplingGraph,
    RoleGender,
    STUDENT_TO_ROLE_GENDER_MAP,
)

GENDER_PREFERENCE_WEIGHT = 10
NEUTRAL_PREFERENCE_WEIGHT = 1


class Calculator:
    def __init__(
        self,
        roles: set[Role],
        students: set[Student],
        role_couplings: RoleCouplingGraph = None,
        essential_roles: set[Role] = None,
    ):
        self.roles = roles
        self.essential_roles = set([]) if essential_roles is None else essential_roles
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

        self.wcnf = WCNFPlus()
        self._every_student_has_exactly_one_role()
        self._students_have_pairwise_different_roles()
        self._enforce_gender_vetoes()
        self._apply_gender_preferences()
        if role_couplings is not None:
            self._set_role_couplings(role_couplings)
        if essential_roles is not None:
            self._enforce_essential_roles(essential_roles)

    def _fill_variable_pool(self, roles: set[Role], students: set[Student]):
        for s in students:
            for r in roles:
                self.variable_pool.id((s, r))

    def _student_has_role(self, s: Student, r: Role):
        return self.variable_pool.id((s, r))

    def _every_student_has_exactly_one_role(self):
        """
        Extends the CNF formula with clauses, which state that
        every student must have exactly one role.
        """
        for student in self.students:
            relevant_variables = []
            for role in self.roles:
                relevant_variables.append(self._student_has_role(student, role))
            self.wcnf.append([relevant_variables, 1], is_atmost=True)
            self.wcnf.append(relevant_variables)

    def _students_have_pairwise_different_roles(self):
        """
        Extends the CNF formula with clauses, which state that
        the roles of students must be pairwise different.
        """
        for this_role in self.roles:
            relevant_variables = []
            for this_student in self.students:
                relevant_variables.append(
                    self._student_has_role(this_student, this_role)
                )
            self.wcnf.append([relevant_variables, 1], is_atmost=True)

    def _enforce_gender_vetoes(self):
        """
        Extends the CNF with negative literals, which ban
        a student from taking over the role of a certain gender.
        :return: a list of literals, which represent all the students' vetoes.
        """
        for this_student in self.students:
            for vetoed_gender in this_student.get_vetoed_genders():
                for vetoed_role in self._roles_with_gender[vetoed_gender]:
                    self.wcnf.append(
                        [-1 * self._student_has_role(this_student, vetoed_role)]
                    )

    def _set_role_couplings(self, role_couplings: RoleCouplingGraph):
        """
        Extends the CNF formula with clauses, which state that given roles are coupled to one another other.
        """
        for role in role_couplings.map.keys():
            for coupled_role in role_couplings.map[role]:
                self._couple_roles(role, coupled_role)

    def _couple_roles(self, role: Role, coupled_role: Role):
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
            self.wcnf.append(
                [-1 * self._student_has_role(this_student, role)] + relevant_variables
            )

    def _enforce_essential_roles(self, essential_roles):
        for role in essential_roles:
            relevant_variables = []
            for student in self.students:
                relevant_variables.append(self._student_has_role(student, role))
            self.wcnf.append(relevant_variables)

    def _apply_gender_preferences(self):
        for student in self.students:
            matching_gender_clause = []
            for preferred_role in self._roles_with_gender.get(
                STUDENT_TO_ROLE_GENDER_MAP.get(student.gender)
            ):
                matching_gender_clause.append(
                    self._student_has_role(student, preferred_role)
                )
            if matching_gender_clause:
                self.wcnf.append(
                    matching_gender_clause, weight=GENDER_PREFERENCE_WEIGHT
                )

            neutral_gender_clause = []
            for neutral_role in self._roles_with_gender.get(RoleGender.NEUTRAL):
                neutral_gender_clause.append(
                    self._student_has_role(student, neutral_role)
                )
            if neutral_gender_clause:
                self.wcnf.append(
                    neutral_gender_clause, weight=NEUTRAL_PREFERENCE_WEIGHT
                )

    def calculate_role_assignments(self) -> dict[Student, Role]:
        if len(self.students) > len(self.roles):
            raise RuntimeError(
                "There are more roles than students! An assignment is obviously impossible!"
            )
        if len(self.essential_roles) > len(self.students):
            raise RuntimeError(
                "There are more essential roles than students! An assignment is obviously impossible!"
            )
        with RC2Stratified(self.wcnf, solver="gluecard4") as solver:
            sat = solver.compute()
            if sat:
                print("Role Assignment Found")
                return self._interpret_model(solver.model)
            else:
                print("Role Assignment Could Not Be Found")
                return {}

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
