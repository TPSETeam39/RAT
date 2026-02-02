from dataclasses import dataclass
from typing import Tuple

from enum import StrEnum, IntEnum


class StudentGender(StrEnum):
    FEMALE = "FEMALE"
    MALE = "MALE"
    NON_BINARY = "NON-BINARY"


class RoleGender(StrEnum):
    FEMALE = "FEMALE"
    MALE = "MALE"
    NON_BINARY = "NON-BINARY"
    NEUTRAL = "NEUTRAL"


class GenderVetoOption(IntEnum):
    NON_BINARY_ONLY = 0
    MALE_ONLY = 1
    FEMALE_ONLY = 2
    MALE_AND_NON_BINARY = 3
    FEMALE_AND_NON_BINARY = 4
    FEMALE_AND_MALE = 5
    NO_VETOES = 6


def get_set_from_gender_veto_option(
    gender_veto_option: GenderVetoOption,
) -> set[RoleGender]:
    match gender_veto_option:
        case GenderVetoOption.NON_BINARY_ONLY:
            return {RoleGender.NON_BINARY}
        case GenderVetoOption.MALE_ONLY:
            return {RoleGender.MALE}
        case GenderVetoOption.FEMALE_ONLY:
            return {RoleGender.FEMALE}
        case GenderVetoOption.MALE_AND_NON_BINARY:
            return {RoleGender.MALE, RoleGender.NON_BINARY}
        case GenderVetoOption.FEMALE_AND_NON_BINARY:
            return {RoleGender.FEMALE, RoleGender.NON_BINARY}
        case GenderVetoOption.FEMALE_AND_MALE:
            return {RoleGender.FEMALE, RoleGender.MALE}
        case GenderVetoOption.NO_VETOES:
            return set([])


@dataclass(frozen=True)
class Role:
    """
    This class represents a single role from the input table.
    The gender of a role is neutral by default.
    """

    id: int
    name: str = "NONAME"
    gender: RoleGender = RoleGender.NEUTRAL

    def __repr__(self):
        return f"Role ({self.id}) {self.name}: gender={self.gender}"


@dataclass(frozen=True)
class Student:
    """
    This class represents a single student from the input table.
    Every student prefers gender-neutral roles by default; he also has no gender vetoes by default.
    """

    id: int
    gender: StudentGender
    first_name: str = "NONAME"
    last_name: str = "NONAME"
    gender_veto_option: GenderVetoOption = GenderVetoOption.NO_VETOES

    def __post_init__(self):
        object.__setattr__(
            self,
            "vetoed_genders",
            get_set_from_gender_veto_option(self.gender_veto_option),
        )

    def get_vetoed_genders(self) -> set[RoleGender]:
        return self.vetoed_genders

    def __repr__(self):
        return (
            f"Student ({self.id}) "
            f"{self.first_name} {self.last_name}: "
            f"veto_option={self.gender_veto_option.name}, "
            f"preferred_gender={str(self.gender)}"
        )


class RoleCouplingGraph:
    """
    This class represents the dependencies between roles through an undirected graph.

    A 'coupling' in this case means that a role can only be taken by at least one student,
    if all the roles, to which said role is coupled, are also taken by at least one student, and vice versa.

    This undirected graph is saved as a dictionary, where the key is a role and the value is a set of roles, to which
    said role is coupled.
    """

    def __init__(self, couplings: list[Tuple[Role, Role]]):
        self.map = self._get_graph_map(couplings)

    def _get_graph_map(self, couplings: list[Tuple[Role, Role]]):
        present_nodes: set[Role] = set([])
        for coupling in couplings:
            present_nodes.add(coupling[0])
            present_nodes.add(coupling[1])

        graph_map: dict[Role, set[Role]] = {}
        for node in present_nodes:
            graph_map[node] = set([])

        for coupling in couplings:
            graph_map[coupling[0]].add(coupling[1])
            graph_map[coupling[1]].add(coupling[0])
        return graph_map
