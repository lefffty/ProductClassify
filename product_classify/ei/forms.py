from django.forms import (
    ModelForm,
    FloatField,
    CharField,
    ModelChoiceField,
)
from django.core.validators import MinValueValidator

from core.mixins import CycleCheckFormMixin

from ei.models import Ei
from ei.constants import EiConsts, Markers
from ei.errors import EiErrors


class EiForm(
    CycleCheckFormMixin,
    ModelForm,
):
    cycle_check_field = "main_class"
    cycle_check_error_msg = EiErrors.CYCLE_DETECTED
    cycle_check_marker = Markers.CYCLE_DETECTED

    convert_factor = FloatField(
        label="Множитель для перевода",
        validators=[
            MinValueValidator(
                EiConsts.CONVERT_FACTOR_MIN_VALUE,
                message=EiErrors.NEGATIVE_FACTOR,
            )
        ],
        required=True,
        error_messages={
            "required": EiErrors.EMPTY_FACTOR,
        },
    )
    name = CharField(
        max_length=EiConsts.NAME_MAX_LENGTH,
        required=True,
        label="Название единицы измерения",
        error_messages={"required": EiErrors.EMPTY_NAME},
    )
    short_name = CharField(
        max_length=EiConsts.SHORT_NAME_MAX_LENGTH,
        required=True,
        label="Сокращенное название единицы измерения",
        error_messages={
            "required": EiErrors.EMPTY_SHORT_NAME,
        },
    )
    main_class = ModelChoiceField(
        queryset=Ei.objects.none(),
        required=False,
        label="Родительская единица измерения",
        empty_label="Выберите родительскую единицу измерения",
    )
    code = CharField(
        max_length=EiConsts.CODE_MAX_LENGTH,
        required=False,
        label="Код единицы измерения",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["main_class"].queryset = Ei.objects.all()

    class Meta:
        model = Ei
        fields = [
            "name",
            "short_name",
            "code",
            "convert_factor",
            "main_class",
        ]
        labels = {
            "name": "Название единицы измерения",
            "short_name": "Сокращенное название единицы измерения",
            "code": "Код единицы измерения",
            "convert_factor": "Множитель для перевода в другую единицу измерения",
            "main_class": "Родитель единицы измерения",
        }
