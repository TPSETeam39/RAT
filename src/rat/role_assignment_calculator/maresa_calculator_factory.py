from ..io import Student
from .calculator import Calculator
from .constants import (
    STUDENT_CAP,
    STUDENT_FLOOR,
    ROLES,
    COUPLINGS,
    get_essential_roles,
    get_priority_roles,
    get_black_listed_roles,
)


def get_calculator(students: set[Student]) -> Calculator | None:
    """
    Returns a calculator for the given students.
    """
    number_of_students = len(students)
    if number_of_students > STUDENT_CAP or number_of_students < STUDENT_FLOOR:
        return None
    return Calculator(
        set(ROLES),
        students,
        COUPLINGS,
        get_essential_roles(number_of_students),
        get_priority_roles(number_of_students),
        get_black_listed_roles(number_of_students),
    )
