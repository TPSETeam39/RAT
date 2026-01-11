from ..calculator import Calculator
from ..calculator_io import Student, Role, RoleAssignment, RoleCouplingGraph
from role_assignment_calculator.genders import Gender, GenderVetoOption
import unittest


def debug_print_role_assignments(role_assignments: set[RoleAssignment]):
    for assignment in role_assignments:
        print(
            f"Student {assignment.student.student_name} was assigned {assignment.assigned_role.role_name}"
        )


def role_is_occupied(role, role_assignments):
    output = False
    for assignment in role_assignments:
        if role == assignment.assigned_role:
            return True
    return output


class TestCalculator(unittest.TestCase):

    def test_determinism(self):
        # GIVEN
        roles = set([Role(f"Role{i}") for i in range(1, 31)])
        students = set([Student(f"Student{i}") for i in range(1, 10)])
        calculator_one = Calculator(roles, students)
        calculator_two = Calculator(roles, students)

        # WHEN
        role_assignments_one = calculator_one.calculate_role_assignments()
        role_assignments_two = calculator_two.calculate_role_assignments()

        # THEN
        self.assertTrue(role_assignments_one != set([]))
        self.assertTrue(role_assignments_two != set([]))
        reference = set(role_assignments_one)
        for assignment in role_assignments_two:
            self.assertTrue(assignment in reference)

    def test_more_roles_than_students(self):
        # GIVEN
        roles = set([Role(f"Role{i}") for i in range(1, 31)])
        students = set([Student(f"Student{i}") for i in range(1, 10)])
        calculator = Calculator(roles, students)

        # WHEN
        role_assignments = calculator.calculate_role_assignments()

        # THEN
        self.assertTrue(role_assignments != set([]))
        self.check_pairwise_distinct(role_assignments)
        self.check_no_vetoes_were_violated(role_assignments)

    def test_equal_number_of_students_and_roles(self):
        # GIVEN
        roles = set([Role(f"Role{i}") for i in range(1, 31)])
        students = set([Student(f"Student{i}") for i in range(1, 31)])
        self.calculator = Calculator(roles, students)

        # WHEN
        role_assignments = self.calculator.calculate_role_assignments()

        # THEN
        self.assertTrue(role_assignments != set([]))
        self.check_pairwise_distinct(role_assignments)
        self.check_no_vetoes_were_violated(role_assignments)

    def test_more_students_than_roles(self):
        # GIVEN
        roles = set([Role(f"Role{i}") for i in range(1, 20)])
        students = set([Student(f"Student{i}") for i in range(1, 31)])
        calculator = Calculator(roles, students)

        # WHEN / THEN
        self.assertRaises(RuntimeError, lambda: calculator.calculate_role_assignments())

    def test_gender_vetoes(self):
        # GIVEN
        gender_neutral_roles = set([Role(f"NeutralRole{i}") for i in range(1, 16)])
        male_roles = set([Role(f"MaleRole{i}", Gender.MALE) for i in range(1, 16)])
        female_roles = set(
            [Role(f"FemaleRole{i}", Gender.FEMALE) for i in range(1, 16)]
        )
        non_binary_roles = set(
            [Role(f"NonBinaryRole{i}", Gender.NON_BINARY) for i in range(1, 16)]
        )

        males = set(
            [
                Student(f"MaleStudent{i}", GenderVetoOption.FEMALE_ONLY, Gender.MALE)
                for i in range(1, 16)
            ]
        )
        females = set(
            [
                Student(f"FemaleStudent{i}", GenderVetoOption.MALE_ONLY, Gender.FEMALE)
                for i in range(1, 16)
            ]
        )
        non_binaries = set(
            [
                Student(
                    f"NonBinaryStudent{i}",
                    GenderVetoOption.FEMALE_AND_MALE,
                    Gender.NON_BINARY,
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
        self.assertTrue(role_assignments != set([]))
        self.check_pairwise_distinct(role_assignments)
        self.check_no_vetoes_were_violated(role_assignments)

    def test_essential_roles(self):
        # GIVEN
        roles = set([Role(f"Role{i}") for i in range(1, 31)])
        essential_roles = set([Role(f"Role{i}") for i in range(1, 10)])
        students = set([Student(f"Student{i}") for i in range(1, 10)])
        calculator = Calculator(roles, students, essential_roles=essential_roles)

        # WHEN
        role_assignments = calculator.calculate_role_assignments()

        # THEN
        self.assertTrue(role_assignments != set([]))
        self.check_pairwise_distinct(role_assignments)
        self.check_no_vetoes_were_violated(role_assignments)
        self.check_all_essential_roles_were_fulfilled(role_assignments, essential_roles)

    def test_more_essential_roles_than_students(self):
        # GIVEN
        roles = set([Role(f"Role{i}") for i in range(1, 31)])
        essential_roles = set([Role(f"Role{i}") for i in range(1, 10)])
        students = set([Student(f"Student{i}") for i in range(1, 5)])
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
        roles = [Role(f"Role{i}") for i in range(1, 31)]
        essential_roles = {roles[0]}
        role_coupling_graph = RoleCouplingGraph(
            [
                (roles[0], roles[1]),
                (roles[1], roles[2]),
                (roles[2], roles[3]),
                (roles[3], roles[4]),
            ]
        )
        students = set([Student(f"Student{i}") for i in range(1, 6)])
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
        self.assertTrue(role_assignments != set([]))
        self.check_pairwise_distinct(role_assignments)
        self.check_all_essential_roles_were_fulfilled(role_assignments, essential_roles)
        for n in range(1, 5):
            self.assertTrue(role_is_occupied(roles[n], role_assignments))

    def check_pairwise_distinct(self, role_assignments: set[RoleAssignment]):
        for a in role_assignments:
            for b in role_assignments:
                if a.student != b.student:
                    self.assertTrue(
                        a.assigned_role != b.assigned_role,
                        f"{a.student} and {b.student}"
                        f" were both assigned {b.assigned_role}!",
                    )

    def check_no_vetoes_were_violated(self, role_assignments: set[RoleAssignment]):
        for assignment in role_assignments:
            vetoed_genders_msg = [
                vetoed_gender for vetoed_gender in assignment.student.vetoed_genders
            ]
            self.assertTrue(
                assignment.assigned_role.gender
                not in assignment.student.vetoed_genders,
                f"{assignment.student.student_name} was assigned {assignment.assigned_role.role_name}, "
                f"but they were against the genders {str(vetoed_genders_msg)}; "
                f"the role has gender {assignment.assigned_role.gender}",
            )

    def check_all_essential_roles_were_fulfilled(
        self, role_assignments: set[RoleAssignment], essential_roles: set[Role]
    ):
        for essential in essential_roles:
            self.assertTrue(role_is_occupied(essential, role_assignments))


if __name__ == "__main__":
    unittest.main()
