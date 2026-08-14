from enum import StrEnum


class ClassStructErrors(StrEnum):
    EMPTY_MAIN_CLASS_ERROR = "Поле для родительского класса необходимо заполнить"
    EMPTY_NAME_ERROR = "Поле для названия класса необходимо заполнить"
    CLASSIFICATOR_CYCLE_ERROR = "При изменении класса в классификаторе образовывается цикл!"


class ParClassErrors:
    ENUM_AGGREGATE_RANGE_ERROR = (
        "Для параметра '{}' типа 'Перечисление' не допускается указывать "
        "минимальное и максимальное значения."
        " Оставьте поля min_value и max_value пустыми."
    )
    MIN_GE_MAX = "У численного параметра минимальное значение должно быть меньше максимального!"
    EMPTY_CLASS_FIELD = "Поле 'Класс изделия' обязательно для заполнения."
    EMPTY_PAR_FIELD = "Поле 'Параметр' обязательно для заполнения."
    AGREGAT_PAR_TYPE = "Поле 'Параметр' не может быть типа 'Аргерат'"


class ChangeParClassErrors(StrEnum):
    EMPTY_FIRST_PAR = "Поле class_field_1 не может быть пустым"
    EMPTY_SECOND_PAR = "Поле class_field_2 не может быть пустым"
    EQUAL_PAR = "Классы изделия не могут быть одинаковыми!"
