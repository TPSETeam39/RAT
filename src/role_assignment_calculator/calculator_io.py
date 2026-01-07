from enum import StrEnum
from dataclasses import dataclass, field

from scipy.stats import studentized_range


class Genders(StrEnum):
    NON_BINARY = 'NON-BINARY'
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    NEUTRAL = 'NEUTRAL'

class Role:
    """
    This class represents a single role from the input table.
    """
    def __init__(self, role_name: str, gender: Genders, dependent_roles=None):
        self.role_name = role_name
        self.gender = gender
        self.dependent_roles = set([]) if dependent_roles is None else {dependent_roles}

class Student:
    """
    This class represents a single student from the input table.
    Every student prefers gender-neutral roles by default.
    """
    def __init__(self, student_name: str, vetoed_genders: set[Genders], preferred_gender: set[Genders]):
        self.student_name = student_name
        self.vetoed_genders = vetoed_genders
        self.preferred_gender = preferred_gender

class RoleAssignment:
    """
    This class represents a single assignment of a student to a role.
    """
    def __init__(self, student: str, assigned_role: str):
        self.student_name = student
        self.assigned_role_name = assigned_role
