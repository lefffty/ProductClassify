from django.forms import (
    ModelForm,
    FloatField,
    CharField,
)

from .models import Ei
from .validators import validate_positive


class EiForm(ModelForm):
    convert_factor = FloatField(
        label='Множитель для перевода',
        validators=[validate_positive,]
    )
    name = CharField(
        max_length=75,
        required=True,
        label='Название единицы измерения',
    )
    short_name = CharField(
        max_length=15,
        required=True,
        label='Сокращенное название единицы измерения',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['main_class'].queryset = Ei.objects.all()

    class Meta:
        model = Ei
        fields = [
            'name', 'short_name',
            'code', 'convert_factor',
            'main_class',
        ]
        labels = {
            'name': 'Название единицы измерения',
            'short_name': 'Сокращенное название единицы измерения',
            'code': 'Код единицы измерения',
            'convert_factor': '''Множитель для перевода в другую
            единицу измерения''',
            'main_class': 'Родитель единицы измерения',
        }
