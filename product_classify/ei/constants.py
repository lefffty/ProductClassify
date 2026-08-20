from enum import IntEnum
from decimal import Decimal


class EiConsts(IntEnum):
    NAME_MAX_LENGTH = 30
    SHORT_NAME_MAX_LENGTH = 8
    CODE_MAX_LENGTH = 5
    CONVERT_FACTOR_MIN_VALUE = Decimal("0.0")

KILOGRAM_ID = 4
