from enum import StrEnum

from route_tech.constants import ProdOperationPosConsts


class EASErrors(StrEnum):
    EMPTY_NAME = (
        "Поле названия субъекта экономической деятельности необходимо заполнить"
    )
    EMPTY_SHORT_NAME = "Поле сокращенного названия субъекта экономической деятельности необходимо заполнить"
    EMPTY_MAIN_CLASS = (
        "Поле для класс субъекта экономической деятельности необходимо заполнить"
    )


class GWCErrors(StrEnum):
    EMPTY_NAME = "Поле для названия группового рабочего центра"
    EMPTY_SHORT_NAME = (
        "Поле для название сокращенного название группового рабочего центра"
    )
    EMPTY_MAIN_CLASS = "Поле для ссылка на родительский класс"
    EMPTY_EAS = "Поле для ссылки на субъект экономической деятельности"
    EMPTY_PLACE = "Поле для количества рабочих мест на групповом рабочем центре"


class ProdOperErrors:
    EMPTY_PROD = "Поле для изделия необходимо заполнить"
    EMPTY_TECH_OPER = "Поле для операции необходимо заполнить"
    EMPTY_PROFESSION = "Поле для профессии рабочего необходимо заполнить"
    EMPTY_CENTER = "Поле для группового рабочего центра необходимо заполнить"
    EMPTY_QUALIFICATION = "Поле для квалификации рабочего необходимо заполнить"
    EMPTY_NUM_WORKERS = "Поле для количества исполнителей необходимо заполнить"


class ProdOperationPosErrors:
    EMPTY_INPUT_PROD_OPER = (
        "Поле для входной пары <Изделие-операция> необходимо заполнить"
    )
    EMPTY_OUTPUT_PROD_OPER = (
        "Поле для выходной пары <Изделие-операция> необходимо заполнить"
    )
    EMPTY_INPUT_QUANTITY = "Поле для расхода входного ресурса необходимо заполнить"
    EMPTY_OUTPUT_QUANTITY = "Поле для количества выходного ресурса необходимо заполнить"
    INVALID_INPUT_QUANTITY = (
        f"Значение не может быть меньше {ProdOperationPosConsts.MIN_VALUE}"
    )
    INVALID_OUTPUT_QUANTITY = (
        f"Значение не может быть меньше {ProdOperationPosConsts.MIN_VALUE}"
    )
