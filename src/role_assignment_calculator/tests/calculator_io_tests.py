import unittest

from ..calculator_io import Role, Student, RoleAssignment
from ..genders import Gender

class CalculatorIOTests(unittest.TestCase):
    """
    These tests are closer to sanity checks than unit tests.
    """

    def test_role_equality(self):
        # GIVEN
        role1 = Role("Role One", Gender.FEMALE)
        role2 = Role("Role One", Gender.FEMALE)
        role3 = Role("Role One", Gender.MALE)
        role4 = Role("role One", Gender.MALE)
        role5 = role1

        # WHEN / THEN
        self.assertTrue(role1 == role2) # Roles are equal when their values are equal
        self.assertTrue(role1 is not role2) # Even if they're equal doesn't mean they're the same object in memory
        self.assertTrue(hash(role1) == hash(role2)) # Same object, same hash
        self.assertTrue(role1 != role3) # Roles differ by gender
        self.assertTrue(role4 != role3) # Role names are case-sensitive
        self.assertTrue(role5 is role1)

    def test_student_equality(self):
        # GIVEN
        student1 = Student("Stud1", preferred_gender=Gender.MALE)
        student2 = Student("Stud1", preferred_gender=Gender.MALE)
        student3 = Student("Stud2", preferred_gender=Gender.FEMALE)

        # WHEN / THEN
        self.assertTrue(student1 == student2)
        self.assertTrue(student1 is not student2)
        self.assertTrue(hash(student2) == hash(student1))
        self.assertTrue(student1 != student3)

    def test_role_assignment_equality(self):
        # GIVEN
        role1 = Role("Role One", Gender.FEMALE)
        role2 = Role("Role One", Gender.FEMALE)
        student1 = Student("Stud1", preferred_gender=Gender.MALE)
        student2 = Student("Stud1", preferred_gender=Gender.MALE)
        assignment1 = RoleAssignment(student1, role1)
        assignment2 = RoleAssignment(student2, role2)

        # WHEN / THEN
        self.assertTrue(assignment2 == assignment1)
        self.assertTrue(assignment2 is not assignment1)
