from dataclasses import dataclass
from typing import Tuple, Dict

from .genders import Gender, GenderVetoOption, get_set_from_gender_veto_option
import copy

@dataclass(frozen=True)
class Role:
    """
    This class represents a single role from the input table.
    The gender of a role is neutral by default.
    """
    role_name: str
    gender: Gender = Gender.NEUTRAL


@dataclass(frozen=True)
class Student:
    """
    This class represents a single student from the input table.
    Every student prefers gender-neutral roles by default; he also has no gender vetoes by default.
    """
    student_name: str
    gender_veto_option: GenderVetoOption = GenderVetoOption.NO_VETOES
    preferred_gender: Gender = Gender.NEUTRAL

    def __post_init__(self):
        object.__setattr__(self, "vetoed_genders", get_set_from_gender_veto_option(self.gender_veto_option))

@dataclass(frozen=True)
class RoleAssignment:
    """
    This class represents a single assignment of a student to a role.
    """
    student: Student
    assigned_role: Role

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
