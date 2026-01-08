from .genders import Gender, GenderVetoOption, get_set_from_gender_veto_option


class Role:
    """
    This class represents a single role from the input table.
    The gender of a role is neutral by default.
    """

    def __init__(self, role_name: str, gender: Gender = Gender.NEUTRAL):
        self.role_name = role_name
        self.gender = gender

    def __eq__(self, other):
        return other.role_name == self.role_name and other.gender == self.gender

    def __hash__(self):
        return hash((self.role_name, self.gender))


class Student:
    """
    This class represents a single student from the input table.
    Every student prefers gender-neutral roles by default; he also has no gender vetoes by default.
    """

    def __init__(
        self,
        student_name: str,
        gender_veto_option: GenderVetoOption = GenderVetoOption.NO_VETOES,
        preferred_gender: Gender = Gender.NEUTRAL,
    ):
        self.student_name = student_name
        self.preferred_gender = preferred_gender
        self._gender_veto_option = gender_veto_option
        self.vetoed_genders = get_set_from_gender_veto_option(gender_veto_option)

    def __eq__(self, other):
        return (
            other.student_name == self.student_name
            and other.vetoed_genders == self.vetoed_genders
            and other.preferred_gender == self.preferred_gender
        )

    def __hash__(self):
        return hash(
            (self.student_name, self._gender_veto_option, self.preferred_gender)
        )


class RoleAssignment:
    """
    This class represents a single assignment of a student to a role.
    """

    def __init__(self, student: Student, assigned_role: Role):
        self.student = student
        self.assigned_role = assigned_role

    def __eq__(self, other):
        return (
            other.student == self.student and other.assigned_role == self.assigned_role
        )

    def __hash__(self):
        return hash((self.student, self.assigned_role))


class RoleDependencyGraph:
    """
    This class represents the dependencies between roles through a directed graph.
    """

    def __init__(self, nodes, dependencies):
        pass
