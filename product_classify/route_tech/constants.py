from enum import IntEnum


class EASConsts(IntEnum):
    NAME_MAX_LENGTH = 100
    SHORT_NAME_MAX_LENGTH = 16


class GWCConsts(IntEnum):
    NAME_MAX_LENGTH = 100
    SHORT_NAME_MAX_LENGTH = 16


class ProdOperConsts(IntEnum):
    T_PZ_DEFAULT = 1.0
    T_SHT_DEFAULT = 1.0
