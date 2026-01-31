from ..calculator import Calculator
from rat.io import (
    Student,
    Role,
    RoleCouplingGraph,
    RoleGender,
    GenderVetoOption,
    StudentGender,
)
import unittest


def debug_print_role_assignments(role_assignments: dict[Student, Role]):
    for student, role in role_assignments.items():
        print(f"{student} was assigned {role}")


def role_is_occupied(role, role_assignments: dict[Student, Role]):
    for assigned_role in role_assignments.values():
        if role == assigned_role:
            return True
    return False


class TestCalculator(unittest.TestCase):

    def test_determinism(self):
        # GIVEN
        roles = set([Role(i) for i in range(1, 31)])
        students = set([Student(i, StudentGender.NON_BINARY) for i in range(1, 10)])
        calculator_one = Calculator(roles, students)
        calculator_two = Calculator(roles, students)

        # WHEN
        role_assignments_one = calculator_one.calculate_role_assignments()
        role_assignments_two = calculator_two.calculate_role_assignments()
        debug_print_role_assignments(role_assignments_two)

        # THEN
        self.assertTrue(len(role_assignments_one) > 0)
        self.assertTrue(len(role_assignments_two) > 0)
        for stud, role in role_assignments_one.items():
            self.assertTrue(role_assignments_two[stud] == role)

    def test_more_roles_than_students(self):
        # GIVEN
        roles = set([Role(i) for i in range(1, 31)])
        students = set([Student(i, StudentGender.NON_BINARY) for i in range(1, 10)])
        calculator = Calculator(roles, students)

        # WHEN
        role_assignments = calculator.calculate_role_assignments()

        # THEN
        self.assertTrue(len(role_assignments) > 0)
        self.check_pairwise_distinct(role_assignments)
        self.check_no_vetoes_were_violated(role_assignments)

    def test_equal_number_of_students_and_roles(self):
        # GIVEN
        roles = set([Role(i) for i in range(1, 31)])
        students = set([Student(i, StudentGender.NON_BINARY) for i in range(1, 31)])
        self.calculator = Calculator(roles, students)

        # WHEN
        role_assignments = self.calculator.calculate_role_assignments()

        # THEN
        self.assertTrue(len(role_assignments) > 0)
        self.check_pairwise_distinct(role_assignments)
        self.check_no_vetoes_were_violated(role_assignments)

    def test_more_students_than_roles(self):
        # GIVEN
        roles = set([Role(i) for i in range(1, 20)])
        students = set([Student(i, StudentGender.NON_BINARY) for i in range(1, 31)])
        calculator = Calculator(roles, students)

        # WHEN / THEN
        self.assertRaises(RuntimeError, lambda: calculator.calculate_role_assignments())

    def test_gender_vetoes(self):
        # GIVEN
        gender_neutral_roles = set([Role(i) for i in range(1, 16)])
        male_roles = set([Role(i, gender=RoleGender.MALE) for i in range(1, 16)])
        female_roles = set([Role(i, gender=RoleGender.FEMALE) for i in range(1, 16)])
        non_binary_roles = set(
            [Role(i, gender=RoleGender.NON_BINARY) for i in range(1, 16)]
        )

        males = set(
            [
                Student(
                    i,
                    gender=StudentGender.MALE,
                    gender_veto_option=GenderVetoOption.FEMALE_ONLY,
                )
                for i in range(1, 16)
            ]
        )
        females = set(
            [
                Student(
                    i,
                    gender=StudentGender.FEMALE,
                    gender_veto_option=GenderVetoOption.MALE_ONLY,
                )
                for i in range(1, 16)
            ]
        )
        non_binaries = set(
            [
                Student(
                    i,
                    gender=StudentGender.NON_BINARY,
                    gender_veto_option=GenderVetoOption.FEMALE_AND_MALE,
                )
                for i in range(1, 16)
            ]
        )
        calculator = Calculator(
            gender_neutral_roles.union(male_roles)
            .union(female_roles)
            .union(non_binary_roles),
            males.union(females).union(non_binaries),
        )

        # WHEN
        role_assignments = calculator.calculate_role_assignments()

        # THEN
        self.assertTrue(len(role_assignments) > 0)
        self.check_pairwise_distinct(role_assignments)
        self.check_no_vetoes_were_violated(role_assignments)

    def test_essential_roles(self):
        # GIVEN
        roles = set([Role(i) for i in range(1, 31)])
        essential_roles = set([Role(i) for i in range(1, 10)])
        students = set([Student(i, StudentGender.NON_BINARY) for i in range(1, 10)])
        calculator = Calculator(roles, students, essential_roles=essential_roles)

        # WHEN
        role_assignments = calculator.calculate_role_assignments()

        # THEN
        self.assertTrue(len(role_assignments) > 0)
        self.check_pairwise_distinct(role_assignments)
        self.check_no_vetoes_were_violated(role_assignments)
        self.check_all_essential_roles_were_fulfilled(role_assignments, essential_roles)

    def test_more_essential_roles_than_students(self):
        # GIVEN
        roles = set([Role(i) for i in range(1, 31)])
        essential_roles = set([Role(i) for i in range(1, 10)])
        students = set([Student(i, StudentGender.NON_BINARY) for i in range(1, 5)])
        calculator = Calculator(roles, students, essential_roles=essential_roles)

        # WHEN / THEN
        self.assertRaises(RuntimeError, lambda: calculator.calculate_role_assignments())

    def test_role_couplings(self):
        """
        This also tests the transitivity of essential roles
        Role1 is essential and coupled to Role2 --> Role2 is also essential
        Role2 is essential and coupled to Role3 --> Role3 is also essential
        Role4 is essential and coupled to Role5 --> Role5 is also essential
        """
        # GIVEN
        roles = [Role(i) for i in range(1, 31)]
        essential_roles = {roles[0]}
        role_coupling_graph = RoleCouplingGraph(
            [
                (roles[0], roles[1]),
                (roles[1], roles[2]),
                (roles[2], roles[3]),
                (roles[3], roles[4]),
            ]
        )
        students = set([Student(i, StudentGender.NON_BINARY) for i in range(1, 6)])
        calculator = Calculator(
            set(roles),
            students,
            role_couplings=role_coupling_graph,
            essential_roles=essential_roles,
        )

        # WHEN
        role_assignments = calculator.calculate_role_assignments()
        debug_print_role_assignments(role_assignments)

        # THEN
        self.assertTrue(len(role_assignments) > 0)
        self.check_pairwise_distinct(role_assignments)
        self.check_all_essential_roles_were_fulfilled(role_assignments, essential_roles)
        for n in range(1, 5):
            self.assertTrue(role_is_occupied(roles[n], role_assignments))

    def check_pairwise_distinct(self, role_assignments: dict[Student, Role]):
        for stud_a, role_a in role_assignments.items():
            for stud_b, role_b in role_assignments.items():
                if stud_a != stud_b:
                    self.assertTrue(
                        role_a != role_b,
                        f"{stud_a} and {stud_b}"
                        f" were both assigned {role_a}!",
                    )

    def check_no_vetoes_were_violated(self, role_assignments: dict[Student, Role]):
        for stud, role in role_assignments.items():
            vetoed_genders_msg = [
                vetoed_gender
                for vetoed_gender in stud.get_vetoed_genders()
            ]
            self.assertTrue(
                role.gender
                not in stud.get_vetoed_genders(),
                f"{stud} was assigned {role}, "
                f"but they were against the genders {str(vetoed_genders_msg)}; "
                f"the role has gender {role.gender}",
            )

    def check_all_essential_roles_were_fulfilled(
        self, role_assignments: dict[Student, Role], essential_roles: set[Role]
    ):
        for essential in essential_roles:
            self.assertTrue(role_is_occupied(essential, role_assignments))


if __name__ == "__main__":
    unittest.main()
