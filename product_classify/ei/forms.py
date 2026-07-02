from django.forms import (
    ModelForm,
    FloatField,
    CharField,
    ModelChoiceField,
)
from django.core.validators import MinValueValidator

from .models import Ei
from .constants import (
    EI_CODE_MAX_LENGTH,
    EI_FORM_NAME_MAX_LENGTH,
    EI_CONVERT_FACTOR_MIN_VALUE,
    EI_FORM_SHORT_NAME_MAX_LENGTH,
)


class EiForm(ModelForm):
    convert_factor = FloatField(
        label="Множитель для перевода",
        validators=[MinValueValidator(EI_CONVERT_FACTOR_MIN_VALUE)],
        required=True,
        error_messages={
            "required": "Поле множителя для перевода в другую единицу измерения необходимо заполнить",
        }
    )
    name = CharField(
        max_length=EI_FORM_NAME_MAX_LENGTH,
        required=True,
        label="Название единицы измерения",
        error_messages={
            "required": "Поле названия единицы измерения необходимо заполнить",
        }
    )
    short_name = CharField(
        max_length=EI_FORM_SHORT_NAME_MAX_LENGTH,
        required=True,
        label="Сокращенное название единицы измерения",
        error_messages={
            "required": "Поле сокращенного названия единицы измерения необходимо заполнить",
        }
    )
    main_class = ModelChoiceField(
        queryset=Ei.objects.none(),
        required=False,
        label="Родительская единица измерения",
        empty_label="Выберите родительскую единицу измерения"
    )
    code = CharField(
        max_length=EI_CODE_MAX_LENGTH,
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
