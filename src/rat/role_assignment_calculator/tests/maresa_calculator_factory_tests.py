import random

from ..maresa_calculator_factory import get_calculator
import unittest

from rat.io import Student, StudentGender, Role, GenderVetoOption


def debug_print_role_assignments(role_assignments: dict[Student, Role]):
    for student, role in role_assignments.items():
        print(f"{student} was assigned {role}")


def get_random_student_gender():
    roll = random.randint(0, 2)
    if roll == 0:
        return StudentGender.NON_BINARY
    elif roll == 1:
        return StudentGender.FEMALE
    elif roll == 2:
        return StudentGender.MALE


def get_random_veto_option():
    roll = random.randint(0, 6)
    return GenderVetoOption(roll)


class MaresaCalculatorFactoryTests(unittest.TestCase):

    def test_return_none_when_too_few_students(self):
        # GIVEN
        students = [Student(i, gender=StudentGender.FEMALE) for i in range(0, 13)]

        # WHEN / THEN
        # The minimum amount is 14
        self.assertIsNone(get_calculator(set(students)))

    def test_return_none_when_too_many_students(self):
        # GIVEN
        students = [Student(i, gender=StudentGender.FEMALE) for i in range(0, 48)]

        # WHEN
        # The maximum amount is 47
        self.assertIsNone(get_calculator(set(students)))

    def test_do_random_testing(self):
        # GIVEN
        n = 15

        # WHEN
        for i in range(0, n):
            students_amount = random.randint(14, 47)
            students = [
                Student(
                    i,
                    gender=get_random_student_gender(),
                    gender_veto_option=get_random_veto_option(),
                )
                for i in range(students_amount)
            ]
            print(f"Trial {i} with {len(students)} students")
            print(students)
            debug_print_role_assignments(
                get_calculator(set(students)).calculate_role_assignments()
            )
