from enum import StrEnum


class ProdErrors(StrEnum):
    EMPTY_CLASS_FIELD = "Поле для родительского класса изделия необходимо заполнить"
    EMPTY_NAME_FIELD = "Поле для названия класса необходимо заполнить"
