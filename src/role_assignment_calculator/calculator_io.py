from enum import StrEnum
from dataclasses import dataclass, field

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

@dataclass
class Student:
    """
    This class represents a single student from the input table.
    Every student prefers gender-neutral roles by default.
    """
    student: str
    vetoed_genders: set[Genders]
    preferred_gender: set[Genders] = field(default_factory=lambda: {Genders.NEUTRAL})

@dataclass
class RoleAssignment:
    """
    This class represents a single assignment of a student to a role.
    """
    student: str
    assigned_role: str
