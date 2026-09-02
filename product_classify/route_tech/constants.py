from enum import IntEnum
from decimal import Decimal


class EASConsts(IntEnum):
    NAME_MAX_LENGTH = 100
    SHORT_NAME_MAX_LENGTH = 16


class GWCConsts(IntEnum):
    NAME_MAX_LENGTH = 100
    SHORT_NAME_MAX_LENGTH = 16


class ProdOperConsts(IntEnum):
    T_PZ_DEFAULT = 1.0
    T_SHT_DEFAULT = 1.0


class ProdOperationPosConsts(IntEnum):
    MIN_VALUE = Decimal("0.0")
    DECIMAL_PLACES = 6
    MAX_DIGITS = 12
