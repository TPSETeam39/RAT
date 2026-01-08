from typing import Tuple

from pysat.formula import IDPool, CNFPlus
from pysat.solvers import Solver

from .calculator_io import Role, Student, RoleAssignment
from .genders import Gender


def parse_student_name_from_assignment(assignment: str) -> str:
    return assignment.split("/")[0]


def parse_role_name_from_assignment(assignment: str) -> str:
    return assignment.split("/")[1]


class Calculator:
    def __init__(self, roles: set[Role], students: set[Student]):
        self.roles = roles
        self.students = students
        self.variable_pool = IDPool()
        self._fill_variable_pool(roles, students)

        self._roles_with_gender = {
            Gender.NON_BINARY: self._get_roles_with_gender(Gender.NON_BINARY),
            Gender.NEUTRAL: self._get_roles_with_gender(Gender.NEUTRAL),
            Gender.MALE: self._get_roles_with_gender(Gender.MALE),
            Gender.FEMALE: self._get_roles_with_gender(Gender.FEMALE),
        }

        self.cnf = CNFPlus()
        self._every_student_has_exactly_one_role()
        self._students_have_pairwise_different_roles()

    def _fill_variable_pool(self, roles: set[Role], students: set[Student]):
        for s in students:
            for r in roles:
                self.variable_pool.id((s, r))

    def _student_has_role(self, s: Student, r: Role):
        return self.variable_pool.id((s, r))

    def _every_student_has_exactly_one_role(self):
        for student in self.students:
            relevant_variables = []
            for role in self.roles:
                relevant_variables.append(self._student_has_role(student, role))
            self.cnf.append(relevant_variables)  # Every student has at least one role
            self.cnf.append(
                [relevant_variables, 1], is_atmost=True
            )  # Every student has at most one role

    def _students_have_pairwise_different_roles(self):
        for this_role in self.roles:
            for this_student in self.students:
                for other_student in self.students:
                    if this_student != other_student:
                        # this_student has this_role --> not(other_student has this role)
                        self.cnf.append(
                            [
                                -1 * self._student_has_role(this_student, this_role),
                                -1 * self._student_has_role(other_student, this_role),
                            ]
                        )

    def _take_gender_vetoes_into_account(self):
        output = []
        for this_student in self.students:
            for vetoed_gender in this_student.vetoed_genders:
                for vetoed_role in self._roles_with_gender[vetoed_gender]:
                    output.append(
                        -1 * self._student_has_role(this_student, vetoed_role)
                    )
        return output

    def calculate_role_assignments(self) -> set[RoleAssignment]:
        if len(self.students) > len(self.roles):
            raise RuntimeError(
                "There are more roles than students! An assignment is obviously impossible!"
            )
        with Solver(name="glucose3", bootstrap_with=self.cnf.clauses) as solver:
            sat = solver.solve(assumptions=self._take_gender_vetoes_into_account())
            if sat:
                print("Role Assignment Found")
                return self._interpret_model(solver.get_model())
            else:
                print("Role Assignment Could Not Be Found")
                return set([])

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
