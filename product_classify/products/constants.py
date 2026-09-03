from enum import IntEnum
from decimal import Decimal


class ProdConsts(IntEnum):
    NAME_MAX_LENGTH = 64
    SHORT_NAME_MAX_LENGTH = 16
    MAX_DIGITS = 12 # стоимость одного изделия не может превышать 999 млрд рублей
    DECIMAL_PLACES = 2 # для хранения копеек
    MIN_COST = Decimal("0.0")


class ParProdConsts(IntEnum):
    INLINE_EXTRA = 1
