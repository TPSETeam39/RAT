from enum import StrEnum, IntEnum


class Gender(StrEnum):
    NON_BINARY = "NON-BINARY"
    MALE = "MALE"
    FEMALE = "FEMALE"
    NEUTRAL = "NEUTRAL"


class GenderVetoOption(IntEnum):
    NON_BINARY_ONLY = (0,)
    MALE_ONLY = (1,)
    FEMALE_ONLY = (2,)
    MALE_AND_NON_BINARY = (3,)
    FEMALE_AND_NON_BINARY = (4,)
    FEMALE_AND_MALE = (5,)
    NO_VETOES = 6


def get_set_from_gender_veto_option(
    gender_veto_option: GenderVetoOption,
) -> set[Gender]:
    match gender_veto_option:
        case GenderVetoOption.NON_BINARY_ONLY:
            return {Gender.NON_BINARY}
        case GenderVetoOption.MALE_ONLY:
            return {Gender.MALE}
        case GenderVetoOption.FEMALE_ONLY:
            return {Gender.FEMALE}
        case GenderVetoOption.MALE_AND_NON_BINARY:
            return {Gender.MALE, Gender.NON_BINARY}
        case GenderVetoOption.FEMALE_AND_NON_BINARY:
            return {Gender.FEMALE, Gender.NON_BINARY}
        case GenderVetoOption.FEMALE_AND_MALE:
            return {Gender.FEMALE, Gender.MALE}
        case GenderVetoOption.NO_VETOES:
            return set([])
