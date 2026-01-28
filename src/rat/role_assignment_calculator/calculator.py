from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNFPlus
from pysat.examples.fm import FM
from pysat.examples.rc2 import RC2, RC2Stratified

from .calculator_io import Role, Student, RoleAssignment, RoleCouplingGraph
from .genders import Gender

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
            Gender.NON_BINARY: self._get_roles_with_gender(Gender.NON_BINARY),
            Gender.NEUTRAL: self._get_roles_with_gender(Gender.NEUTRAL),
            Gender.MALE: self._get_roles_with_gender(Gender.MALE),
            Gender.FEMALE: self._get_roles_with_gender(Gender.FEMALE),
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
            self.wcnf.extend(
                CardEnc.equals(lits=relevant_variables, encoding=EncType.pairwise)
            )

    def _students_have_pairwise_different_roles(self):
        """
        Extends the CNF formula with clauses, which state that
        the roles of students must be pairwise different.
        """
        for this_role in self.roles:
            for this_student in self.students:
                for other_student in self.students:
                    if this_student != other_student:
                        # this_student has this_role implies not(other_student has this role)
                        self.wcnf.append(
                            [
                                -1 * self._student_has_role(this_student, this_role),
                                -1 * self._student_has_role(other_student, this_role),
                            ]
                        )

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
            if student.preferred_gender == Gender.NEUTRAL:
                continue
            for preferred_role in self._get_roles_with_gender(student.preferred_gender):
                self.wcnf.append(
                    [self._student_has_role(student, preferred_role)],
                    weight=GENDER_PREFERENCE_WEIGHT,
                )
            for neutral_role in self._get_roles_with_gender(Gender.NEUTRAL):
                self.wcnf.append(
                    [self._student_has_role(student, neutral_role)],
                    weight=NEUTRAL_PREFERENCE_WEIGHT,
                )

    def calculate_role_assignments(
        self, backend_solver="rc2", print_solve_time=False
    ) -> set[RoleAssignment]:
        if len(self.students) > len(self.roles):
            raise RuntimeError(
                "There are more roles than students! An assignment is obviously impossible!"
            )
        if len(self.essential_roles) > len(self.students):
            raise RuntimeError(
                "There are more essential roles than students! An assignment is obviously impossible!"
            )
        with self._get_solver(backend_solver) as solver:
            sat = solver.compute()
            if print_solve_time:
                print(f"{backend_solver} took {solver.oracle_time()} seconds")
            if sat:
                print("Role Assignment Found")
                return self._interpret_model(solver.model)
            else:
                print("Role Assignment Could Not Be Found")
                return set([])

    def _get_solver(self, solver):
        if solver == "fm":
            return FM(self.wcnf, enc=EncType.pairwise, solver="glucose3", verbose=0)
        elif solver == "rc2":
            return RC2(self.wcnf, solver="glucose3", verbose=0)
        elif solver == "rc2s":
            return RC2Stratified(self.wcnf, solver="glucose3", verbose=0)
        else:
            raise ValueError(f"{solver} is not a supported solver!")

    def _interpret_model(self, model) -> set[RoleAssignment]:
        role_assignments = []
        for variable in model:
            if variable > 0:
                role_assignments.append(self.variable_pool.obj(variable))

        output = set([])
        for ra in role_assignments:
            # The variable pool has a mapping of integer IDs to the tuple defined in assign(s, r)
            output.add(RoleAssignment(ra[0], ra[1]))
        return output

    def _get_roles_with_gender(self, vetoed_gender: Gender):
        output = []
        for role in self.roles:
            if role.gender == vetoed_gender:
                output.append(role)
        return output
