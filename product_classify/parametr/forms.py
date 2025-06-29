from django.forms import (
    ModelForm,
    ModelChoiceField,
    CharField
)
from django.core.exceptions import ValidationError

from classes.models import ClassStruct
from ei.models import Ei
from parametr.models import Parametr
from .constants import (
    IMAGE_ENUMS_ID,
    STRING_ENUMS_ID,
    PARAMETR_FORM_NAME_MAX_LENGTH,
)


class ParametrForm(ModelForm):
    parametr_type = ModelChoiceField(
        label='Тип параметра',
        queryset=ClassStruct.parametr_types.all(),
    )
    par_ei = ModelChoiceField(
        label='Единица измерения параметра',
        queryset=Ei.objects.all(),
        required=False,
    )
    name = CharField(
        max_length=PARAMETR_FORM_NAME_MAX_LENGTH,
        required=True,
        label='Название параметра',
    )

    class Meta:
        model = Parametr
        fields = [
            'parametr_type', 'name',
            'short_name', 'par_ei',
        ]
        labels = {
            'parametr_type': 'Тип параметра',
            'name': 'Название параметра',
            'short_name': 'Сокращенное название параметра',
            'par_ei': 'Единица измерения параметра',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parametr_type'].queryset = ClassStruct.parametr_types.all()
        self.fields['par_ei'].queryset = Ei.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        parametr_tp = cleaned_data.get('parametr_type')
        par_ei = cleaned_data.get('par_ei')

        str_enum = ClassStruct.objects.get(pk=IMAGE_ENUMS_ID)
        img_enum = ClassStruct.objects.get(pk=STRING_ENUMS_ID)

        if parametr_tp == str_enum and par_ei is not None:
            raise ValidationError(
                '''Параметр с типом Перечисление строк
                не может иметь единиц измерения'''
            )
        elif parametr_tp == img_enum and par_ei is not None:
            raise ValidationError(
                '''Параметр с типом Перечисление изображений
                не может иметь единиц измерения'''
            )
        return cleaned_data
