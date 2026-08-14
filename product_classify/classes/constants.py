from enum import IntEnum


class ClassStructConsts(IntEnum):
    NAME_MAX_LENGTH = 128
    SHORT_NAME_MAX_LENGTH = 16


class ProdClassConsts(IntEnum):
    NAME_MAX_LENGTH = 128
    SHORT_NAME_MAX_LENGTH = 16


class EnumClassConsts(IntEnum):
    NAME_MAX_LENGTH = 75
    SHORT_NAME_MAX_LENGTH = 16


class ParClassConsts(IntEnum):
    INLINE_EXTRA = 1
    NUM_MIN_VALUE = 1
    MIN_VALUE_LOWER_BOUND = 0.0
    MAX_VALUE_LOWER_BOUND = 0.0


class EnumsIds(IntEnum):
    PARENT = 14
    STRING = 15
    IMAGE = 16
    NUMERIC = 17
    DOUBLE = 18
    INT = 19


class ParamIds(IntEnum):
    NUMERIC = 26
    DOUBLE = 27
    INT = 28
    AGREGAT = 30


class ProductsConsts(IntEnum):
    PRODUCT_ID = 1
    FASTENER_ID = 2
    NUTS_ID = 5


ENUMS_IDS = [item.value for item in EnumsIds]
PARAMS_IDS = [item.value for item in ParamIds]
NUMERIC_PARAMS = [ParamIds.DOUBLE.value, ParamIds.INT.value]
ENUM_PARAMS = [
    EnumsIds.STRING.value,
    EnumsIds.IMAGE.value,
    EnumsIds.INT.value,
    EnumsIds.DOUBLE.value
]
