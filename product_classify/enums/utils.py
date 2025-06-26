from .models import Enums
from .constants import (
    STRING_ENUMS_ID,
    IMAGE_ENUMS_ID,
    INT_ENUMS_ID,
    DOUBLE_ENUMS_ID,
)


def get_enum_value(enum: Enums):
    enum_type = enum.enum.main_class.id
    if enum_type == STRING_ENUMS_ID:
        return enum.name
    elif enum_type == IMAGE_ENUMS_ID:
        return enum.image
    elif enum_type == INT_ENUMS_ID:
        return enum.int_value
    elif enum_type == DOUBLE_ENUMS_ID:
        return enum.double_value
