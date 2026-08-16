from enum import StrEnum


class ProdErrors(StrEnum):
    EMPTY_CLASS_FIELD = "Поле для родительского класса изделия необходимо заполнить"
    EMPTY_NAME_FIELD = "Поле для названия класса необходимо заполнить"


class CommonParProdErrors:
    EMPTY_PROD_FIELD = "Поле для изделия необходимо заполнить"
    EMPTY_PAR_FIELD = "Поле для параметра необходимо заполнить"
    INVALID_PAR = "Параметр '{}' не принадлежит классу изделия '{}'"


class IntParErrors:
    DOUBLE_FIELD_SPECIFIED = "Для целочисленного параметра нельзя указать значение поля double_value"
    ENUM_FIELD_SPECIFIED = "Для целочисленного параметра нельзя указать значение поля enum_val"
    INT_FIELD_EMPTY = "Для целочисленного параметра изделия необходимо указать значение поля int_value"
    INVALID_RANGE = "Целочисленное значение не входит в границы диапазона(<{:d}, {:d}>)"


class DoubleParErrors:
    INT_FIELD_SPECIFIED = "Для вещественного параметра нельзя указать значение поля int_value"
    ENUM_FIELD_SPECIFIED = "Для вещественного параметра нельзя указать значение поля enum_val"
    DOUBLE_FIELD_EMPTY = "Для вещественного параметра изделия необходимо указать значение поля int_value"
    INVALID_RANGE = "Вещественное значение не входит в границы диапазона(<{:2f}, {:2f}>)"


class EnumsParErrors:
    INT_FIELD_SPECIFIED = "Для параметра-перечисления изделия нельзя указать значение поля int_value"
    DOUBLE_FIELD_SPECIFIED = "Для параметра-перечисления изделия нельзя указать значение поля double_value"
    ENUM_FIELD_EMPTY = "Для параметра-перечисления изделия необходимо указать значение поля enum_val"
