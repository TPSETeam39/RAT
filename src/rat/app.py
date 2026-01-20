import rat
from rat.role_assignment_calculator.calculator import Calculator
from rat.role_assignment_calculator.calculator_io import Role, Student, RoleAssignment

def debug_print_role_assignments(role_assignments: set[RoleAssignment]):
    for assignment in role_assignments:
        print(
            f"Student {assignment.student.name} was assigned {assignment.assigned_role.name}"
        )

# GIVEN
roles = set([Role(f"Role{i}") for i in range(1, 31)])
students = set([Student(f"Student{i}") for i in range(1, 31)])
calculator = Calculator(roles, students)

# WHEN
role_assignments = calculator.calculate_role_assignments()

# THEN
debug_print_role_assignments(role_assignments)

rat.main()