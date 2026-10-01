from enum import IntEnum, StrEnum
from decimal import Decimal


class Markers(StrEnum):
    CYCLE_DETECTED = "[EAS_CYCLE]"


class EASConsts(IntEnum):
    NAME_MAX_LENGTH =       100
    SHORT_NAME_MAX_LENGTH = 16


class GWCConsts(IntEnum):
    NAME_MAX_LENGTH =       100
    SHORT_NAME_MAX_LENGTH = 16
    MIN_PLACE =             1


class ProdOperConsts(IntEnum):
    T_PZ_DEFAULT =          1.0
    T_SHT_DEFAULT =         1.0


class ProdOperationPosConsts(IntEnum):
    MIN_VALUE =         Decimal("0.0")
    DECIMAL_PLACES =    6
    MAX_DIGITS =        12


class FormSetConsts(IntEnum):
    EXTRA =             0


class TechRoutePdfConsts:
    FONT_NAME = "DejaVuSerif"
    FONT_PATH_PARTS = (
        "fonts",
        "DejaVuSerif.ttf"
    )

    LEFT_MARGIN =       20
    RIGHT_MARGIN =      20
    TOP_MARGIN =        30
    BOTTOM_MARGIN =     30

    NORMAL_FONTSIZE =   8
    NORMAL_LEADING =    10
    HEADER_FONTSIZE =   9
    HEADER_ALIGNMENT =  1
    TITLE_FONTSIZE =    14
    TITLE_ALIGNMENT =   1
    TITLE_SPACEAFTER =  12

    CELL_PADDING =      4
    SPACER =            (1, 12)

    HEADER_BG =         "#2c3e50"
    ROW_BG_ALT =        "#f8f9fa"
