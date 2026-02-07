# Hardcode the roles until we can save and load roles
from typing import Any

from rat.io import Role, RoleGender, RoleCouplingGraph

STUDENT_CAP = 48
STUDENT_FLOOR = 14

# KLASSE 8A
ANPU_KRIS = Role(0, name="Anpu,Kris")
APEIRO_SOPHIA = Role(1, name="Apeiro,Sophia", gender=RoleGender.FEMALE)
ASK_CEM = Role(2, name="Ask,Cem", gender=RoleGender.MALE)
FUERST_AMAR = Role(3, name="Fürst,Amar")
HERBST_DAVID = Role(4, name="Herbst,David", gender=RoleGender.MALE)
HERMANN_LOTTE = Role(5, name="Hermann,Lotte", gender=RoleGender.FEMALE)
KLEIN_TONI = Role(6, name="Klein,Toni")
KOCH_ERWIN = Role(7, name="Koch,Erwin", gender=RoleGender.MALE)
LAUTNER_JONA = Role(8, name="Lautner,Jona")
MAIR_JULIUS = Role(9, name="Mair,Julius", gender=RoleGender.MALE)
MITTEMEIER_HANNAH = Role(10, name="Mittemeier,Hannah", gender=RoleGender.FEMALE)
MUELLER_LEO = Role(11, name="Müller,Leo", gender=RoleGender.MALE)
NUBE_FELIPE = Role(12, name="Nube,Felipe", gender=RoleGender.MALE)
RITTERSPRUNG_AVA = Role(13, name="Rittersprung,Ava", gender=RoleGender.MALE)
SERING_AILYN = Role(14, name="Sering,Ailyn (Kim)", gender=RoleGender.NON_BINARY)
SCHMIDT_LUCA = Role(15, name="Schmidt,Luca")
WAGNER_LEONIE = Role(16, name="Wagner,Leonie", gender=RoleGender.FEMALE)

# KLASSE 8B
ZENA_NAYK = Role(17, name="Zena,Nayk", gender=RoleGender.MALE)
BEIL_KARA = Role(18, name="Beil, Kara", gender=RoleGender.FEMALE)
CHRISTMANN_FLO = Role(19, name="Christmann, Flo")
DOMSTOLL_ALEX = Role(20, name="Domstoll, Alex")
FRIEDEN_JOHANNES = Role(21, name="Frieden, Johannes", gender=RoleGender.MALE)
HANKE_ELENA = Role(22, name="Hanke, Elena", gender=RoleGender.FEMALE)
HUBER_LEON = Role(23, name="Huber, Leon", gender=RoleGender.MALE)
JUNG_MARIA = Role(24, name="Jung, Maria", gender=RoleGender.FEMALE)
KNOPF_SINA = Role(25, name="Knopf, Sina", gender=RoleGender.FEMALE)
KRUEGER_MAX = Role(26, name="Krüger, Max", gender=RoleGender.MALE)
LINDA_ISSA = Role(27, name="Linda, Issa")
LIU_WANJA = Role(28, name="Liu, Wanja")
METINER_YAGMUR = Role(29, name="Metiner, Yagmur", gender=RoleGender.MALE)
MUSALAHA_MARTIN = Role(30, name="Musalaha, Martin", gender=RoleGender.MALE)
PIROG_KAMIL = Role(31, name="Pirog, Kamil", gender=RoleGender.MALE)
SCHUBERT_JOSEPHINE = Role(32, name="Schubert, Josephine", gender=RoleGender.FEMALE)
SRECA_MIKE = Role(33, name="Sreca, Mike", gender=RoleGender.MALE)
STUMPF_BENTE = Role(34, name="Stumpf, Bente")
UNHOCH_LILLI = Role(35, name="Unhoch, Lilli", gender=RoleGender.FEMALE)

# SCHULPERSONAL
SCHUL_DEGHAN = Role(36, name="Förderschullehrkraft Deghan")
SCHUL_ALIDOUST = Role(37, name="Lehrkraft Alidoust")
SCHUL_AMARA = Role(38, name="Lehrkraft Amara")
SCHUL_BOEHMER = Role(39, name="Lehrkraft Böhmer")
SCHUL_EMMINGER = Role(40, name="Lehrkraft Emminger")
SCHUL_HANS_MERIC = Role(41, name="Lehrkraft Hans-Meric")
SCHUL_PARK = Role(42, name="Lehkraft im Vorbereitungsdienst Park")
SCHUL_ZOEPFEL = Role(43, name="Lehrkraft Zöpfel")
SCHUL_VON_BUCHTAHL = Role(44, name="Schulleitung von Buchtahl")
SCHUL_ADEYEMI = Role(45, name="Schulsozialarbeit Adeyemi")
SCHUL_MEYER_SEHRING = Role(46, name="Sekretariat Meyer-Sehring")

ROLES = [
    ANPU_KRIS,
    APEIRO_SOPHIA,
    ASK_CEM,
    FUERST_AMAR,
    HERBST_DAVID,
    HERMANN_LOTTE,
    KLEIN_TONI,
    KOCH_ERWIN,
    LAUTNER_JONA,
    MAIR_JULIUS,
    MITTEMEIER_HANNAH,
    MUELLER_LEO,
    NUBE_FELIPE,
    RITTERSPRUNG_AVA,
    SERING_AILYN,
    SCHMIDT_LUCA,
    WAGNER_LEONIE,
    ZENA_NAYK,
    BEIL_KARA,
    CHRISTMANN_FLO,
    DOMSTOLL_ALEX,
    FRIEDEN_JOHANNES,
    HANKE_ELENA,
    HUBER_LEON,
    JUNG_MARIA,
    KNOPF_SINA,
    KRUEGER_MAX,
    LINDA_ISSA,
    LIU_WANJA,
    METINER_YAGMUR,
    MUSALAHA_MARTIN,
    PIROG_KAMIL,
    SCHUBERT_JOSEPHINE,
    SRECA_MIKE,
    STUMPF_BENTE,
    UNHOCH_LILLI,
    SCHUL_DEGHAN,
    SCHUL_ALIDOUST,
    SCHUL_AMARA,
    SCHUL_BOEHMER,
    SCHUL_EMMINGER,
    SCHUL_HANS_MERIC,
    SCHUL_PARK,
    SCHUL_ZOEPFEL,
    SCHUL_VON_BUCHTAHL,
    SCHUL_ADEYEMI,
    SCHUL_MEYER_SEHRING,
]

KLASSE_8A = {
    ASK_CEM,
    KLEIN_TONI,
    KOCH_ERWIN,
    LAUTNER_JONA,
    MAIR_JULIUS,
    MUELLER_LEO,
    ANPU_KRIS,
    APEIRO_SOPHIA,
    FUERST_AMAR,
    HERBST_DAVID,
    HERMANN_LOTTE,
    MITTEMEIER_HANNAH,
    NUBE_FELIPE,
    WAGNER_LEONIE,
    ZENA_NAYK,
}

KLASSE_8B_ESSENTIALS = {
    BEIL_KARA,  # KLASSE 8B
    FRIEDEN_JOHANNES,
    HUBER_LEON,
    KNOPF_SINA,
    KRUEGER_MAX,
    LINDA_ISSA,
    METINER_YAGMUR,
    MUSALAHA_MARTIN,
    STUMPF_BENTE,
    UNHOCH_LILLI,
}

SCHUL_PERSONAL_OHNE_MEYER_SEHRING = {
    SCHUL_DEGHAN,
    SCHUL_ALIDOUST,
    SCHUL_AMARA,
    SCHUL_BOEHMER,
    SCHUL_EMMINGER,
    SCHUL_HANS_MERIC,
    SCHUL_ZOEPFEL,
}

COUPLINGS = None

ESSENTIAL_ROLES = {
    "25-47": KLASSE_8B_ESSENTIALS.union(SCHUL_PERSONAL_OHNE_MEYER_SEHRING).union(
        {
            ASK_CEM,  # KLASSE 8A
            KLEIN_TONI,
            KOCH_ERWIN,
            LAUTNER_JONA,
            MAIR_JULIUS,
            MUELLER_LEO,
            RITTERSPRUNG_AVA,
            SERING_AILYN,
            SCHMIDT_LUCA,
        }
    ),
    "17-24": KLASSE_8B_ESSENTIALS.union(
        {
            SCHUL_DEGHAN,
            SCHUL_ALIDOUST,
            SCHUL_AMARA,
            SCHUL_BOEHMER,
            SCHUL_ZOEPFEL,
        }
    ),
    "14-16": KLASSE_8B_ESSENTIALS.union(
        {
            SCHUL_DEGHAN,
            SCHUL_AMARA,
            SCHUL_BOEHMER,
            SCHUL_PARK,
        }
    ),
}

PRIORITY_ROLES = {
    "25-47": {
        KOCH_ERWIN,  # KLASSE 8A
        MITTEMEIER_HANNAH,
        SCHMIDT_LUCA,
        JUNG_MARIA,  # KLASSE 8B
        LIU_WANJA,
        SRECA_MIKE,
        SCHUL_PARK,  # KLASSE 8C
        SCHUL_VON_BUCHTAHL,
        SCHUL_ADEYEMI,
    },
    "17-24": {SCHUL_PARK, SCHUL_VON_BUCHTAHL},
    "14-16": {SCHUL_VON_BUCHTAHL, SCHUL_ADEYEMI},
}

BLACKLISTED_ROLES = {
    "25-47": {SCHUL_MEYER_SEHRING},
    "17-24": KLASSE_8A.union({SCHUL_EMMINGER, SCHUL_HANS_MERIC, SCHUL_MEYER_SEHRING}),
    "14-16": KLASSE_8A.union(
        {
            SCHUL_ALIDOUST,
            SCHUL_EMMINGER,
            SCHUL_HANS_MERIC,
            SCHUL_ZOEPFEL,
            SCHUL_MEYER_SEHRING,
        }
    ),
}


def _select_from_dictionary(
    number_of_students: int, some_dict: dict[str, set[Any]]
) -> set[Any]:
    if number_of_students == STUDENT_CAP:
        return some_dict["25-47"]
    elif 25 <= number_of_students <= 47:
        return some_dict["25-47"]
    elif 14 <= number_of_students <= 16:
        return some_dict["14-16"]


def get_essential_roles(number_of_students: int) -> set[Role]:
    return _select_from_dictionary(number_of_students, ESSENTIAL_ROLES)


def get_priority_roles(number_of_students) -> set[Role]:
    return _select_from_dictionary(number_of_students, PRIORITY_ROLES)


def get_black_listed_roles(number_of_students) -> set[Role]:
    return _select_from_dictionary(number_of_students, BLACKLISTED_ROLES)
