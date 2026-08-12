from enum import StrEnum


class ClassStructErrors(StrEnum):
    EMPTY_MAIN_CLASS_ERROR = "Поле для родительского класса необходимо заполнить"
    EMPTY_NAME_ERROR = "Поле для названия класса необходимо заполнить"
    CLASSIFICATOR_CYCLE_ERROR = "При изменении класса в классификаторе образовывается цикл!"


class ParClassErrors:
    ENUM_AGGREGATE_RANGE_ERROR = (
        "Для параметра '{}' типа 'Перечисление' или 'Агрегат' не допускается указывать "
        "минимальное и максимальное значения."
        " Оставьте поля min_value и max_value пустыми."
    )
    MIN_GE_MAX = "У численного параметра минимальное значение должно быть меньше максимального!"
