from ..calculator import Calculator
from ..calculator_io import Student, Role, Genders, RoleAssignment
import unittest

class TestCalculator(unittest.TestCase):

    def test_more_roles_than_students(self):
        # GIVEN
        roles = set([
            Role(f"Role{i}",
                 Genders.NEUTRAL)
            for i in range(1, 31)
        ])
        students = set([
            Student(f"Student{i}", set([]), set([]))
            for i in range(1, 10)
        ])
        self.calculator = Calculator(roles, students)

        # WHEN
        role_assignments = self.calculator.calculate_role_assignments()

        # THEN
        self.check_pairwise_distinct(role_assignments)

    def test_equal_number_of_students_and_roles(self):
        # GIVEN
        roles = set([
            Role(f"Role{i}",
                 Genders.NEUTRAL)
            for i in range(1, 31)
        ])
        students = set([
            Student(f"Student{i}", set([]), set([]))
            for i in range(1, 31)
        ])
        self.calculator = Calculator(roles, students)

        # WHEN
        role_assignments = self.calculator.calculate_role_assignments()

        # THEN
        self.check_pairwise_distinct(role_assignments)

    def test_more_students_than_roles(self):
        # GIVEN
        roles = set([
            Role(f"Role{i}",
                 Genders.NEUTRAL)
            for i in range(1, 20)
        ])
        students = set([
            Student(f"Student{i}", set([]), set([]))
            for i in range(1, 31)
        ])
        self.calculator = Calculator(roles, students)

        # WHEN / THEN
        self.assertRaises(RuntimeError, lambda: self.calculator.calculate_role_assignments())

    def check_pairwise_distinct(self, role_assignments: set[RoleAssignment]):
        for a in role_assignments:
            for b in role_assignments:
                if a.student_name != b.student_name:
                    self.assertTrue(a.assigned_role_name != b.assigned_role_name,
                                    f"{a.student_name} and {b.student_name}"
                                    f" were both assigned {b.assigned_role_name}!")

if __name__ == '__main__':
    unittest.main()
