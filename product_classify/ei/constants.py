from enum import IntEnum, StrEnum
from decimal import Decimal


class EiConsts(IntEnum):
    NAME_MAX_LENGTH =           30
    SHORT_NAME_MAX_LENGTH =     8
    CODE_MAX_LENGTH =           5
    CONVERT_FACTOR_MIN_VALUE =  Decimal("0.0")
    DECIMAL_PLACES =            10
    MAX_DIGITS =                20


class Markers(StrEnum):
    CYCLE_DETECTED = "[EI_CYCLE]"


KILOGRAM_ID =                   4
