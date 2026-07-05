from django.forms import ModelForm, ModelChoiceField, CharField
from django.core.exceptions import ValidationError

from classes.models import ClassStruct
from ei.models import Ei
from parametr.models import Parametr

from .constants import (
    IMAGE_ENUMS_ID,
    STRING_ENUMS_ID,
    AGREGAT_TYPE_ID,
    PARAMETR_FORM_NAME_MAX_LENGTH,
    PARAMETR_SHORT_NAME_MAX_LENGTH,
)


class ParametrForm(ModelForm):
    parametr_type = ModelChoiceField(
        label="Тип параметра",
        queryset=ClassStruct.objects.none(),
        required=True,
    )
    par_ei = ModelChoiceField(
        label="Единица измерения параметра",
        queryset=Ei.objects.none(),
        required=False,
    )
    name = CharField(
        max_length=PARAMETR_FORM_NAME_MAX_LENGTH,
        required=True,
        label="Название параметра",
    )
    short_name = CharField(
        max_length=PARAMETR_SHORT_NAME_MAX_LENGTH,
        required=False,
        label="Сокращенное название параметра",
    )

    class Meta:
        model = Parametr
        fields = (
            "parametr_type",
            "name",
            "short_name",
            "par_ei",
        )
        labels = {
            "parametr_type": "Тип параметра",
            "name": "Название параметра",
            "short_name": "Сокращенное название параметра",
            "par_ei": "Единица измерения параметра",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parametr_type"].queryset = ClassStruct.parametr_types()
        self.fields["par_ei"].queryset = Ei.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        parametr_tp = cleaned_data.get("parametr_type")
        par_ei = cleaned_data.get("par_ei")

        str_enum = ClassStruct.objects.get(pk=STRING_ENUMS_ID)
        img_enum = ClassStruct.objects.get(pk=IMAGE_ENUMS_ID)
        agregat_type = ClassStruct.objects.get(pk=AGREGAT_TYPE_ID)

        if parametr_tp == str_enum and par_ei is not None:
            raise ValidationError(
                """Параметр типа 'Перечисление строк' не может иметь единиц измерения"""
            )
        elif parametr_tp == img_enum and par_ei is not None:
            raise ValidationError(
                """Параметр типа 'Перечисление изображений' не может иметь единиц измерения"""
            )
        elif parametr_tp == agregat_type and par_ei is not None:
            raise ValidationError(
                """Параметр типа 'Агрегат' не может иметь единиц измерения"""
            )
        return cleaned_data
