from enum import StrEnum


class AgregatErrors(StrEnum):
    EMPTY_FIRST_PARAM = "Поле первого параметра агрегата в форме необходимо заполнить"
    EMPTY_SECOND_PARAM = "Поле второго параметра агрегата в форме необходимо заполнить"
    SAME_PARAMS = "Выберите разные параметры"
