from django.forms import (
    ModelChoiceField,
    ModelForm,
    Form,
    CharField,
)
from django.core.exceptions import ValidationError

from .models import Enums
from classes.models import ClassStruct
from .constants import (
    INT_ENUMS_ID,
    IMAGE_ENUMS_ID,
    DOUBLE_ENUMS_ID,
    STRING_ENUMS_ID,
    ENUMS_FORM_NAME_MAX_LENGTH,
    ENUMS_FORM_SHORT_NAME_MAX_LENGTH,
)


class EnumsForm(ModelForm):
    enum = ModelChoiceField(
        label='Перечисление',
        queryset=ClassStruct.terminal_enum_classes.all(),
        empty_label='Выберите перечисление',
        required=True,
    )
    picture_value = CharField(
        help_text='Разрешенные форматы изображений: ["jpg", "png"]',
        label='Путь к изображению',
        required=False,
    )
    name = CharField(
        max_length=ENUMS_FORM_NAME_MAX_LENGTH,
        label='Название перечисления',
        required=False,
    )
    short_name = CharField(
        max_length=ENUMS_FORM_SHORT_NAME_MAX_LENGTH,
        required=True,
        label='Сокращенное название перечисления',
    )

    class Meta:
        model = Enums
        fields = [
            'enum', 'name',
            'short_name', 'double_value',
            'int_value', 'picture_value',
        ]
        labels = {
            'enum': 'Родитель перечисления',
            'name': 'Название перечисления',
            'short_name': 'Сокращенное название перечисления',
            'double_value': 'Вещественное значение параметра',
            'int_value': 'Целочисленное значение параметра',
            'picture_value': 'Путь к изображению',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enum'].queryset = ClassStruct.terminal_enum_classes.all()

    def clean(self):
        print('Очистка данных')
        cleaned_data = super().clean()
        picture_value = str(cleaned_data.get('picture_value'))
        enum = cleaned_data.get('enum')
        parent_id = enum.main_class.id
        int_value = cleaned_data['int_value']
        double_value = cleaned_data['double_value']

        if parent_id == STRING_ENUMS_ID:
            if any([picture_value, int_value, double_value]):
                raise ValidationError(
                    '''Значение перечисления строк не должно иметь
                    пути к изображению, целочисленного и вещественного
                    значений'''
                )
        elif parent_id == IMAGE_ENUMS_ID:
            if any([int_value, double_value]):
                raise ValidationError(
                    '''Значение перечисления изображений не должно
                    иметь численных значений'''
                )
            if picture_value is None or not picture_value.endswith(
                ('.jpg', '.png')
            ):
                raise ValidationError(
                    '''Неверный формат изображения!
                    Разрешенные форматы изображений: ["jpg", "png"]'''
                )
        elif parent_id == INT_ENUMS_ID:
            if any([int_value, picture_value]):
                raise ValidationError(
                    '''Вещественное перечисление не должно иметь
                    целочисленного значения и путь к изображению'''
                )
        elif parent_id == DOUBLE_ENUMS_ID:
            if any([double_value, picture_value]):
                raise ValidationError(
                    '''Целочисленное перечисление не должно иметь
                    вещественного значения и путь к изображению'''
                )
        cleaned_data['num'] = Enums.objects.filter(enum=enum).count() + 1
        return cleaned_data

    def save(self, commit=True):
        print('Сохранение данных')
        instance = super().save(commit=False)
        instance.num = self.cleaned_data['num']
        if commit:
            instance.save()
        return instance


class ChangeNumForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enum_1'] = ModelChoiceField(
            queryset=Enums.objects.all(),
            empty_label='Выберите перечисление',
            required=True,
            label='Перечисление 1',
        )
        self.fields['enum_2'] = ModelChoiceField(
            queryset=Enums.objects.all(),
            empty_label='Выберите перечисление',
            required=True,
            label='Перечисление 2',
        )

    def clean(self):
        cleaned_data = super().clean()
        enum_1 = cleaned_data.get('enum_1')
        enum_2 = cleaned_data.get('enum_2')

        if enum_1 == enum_2:
            raise ValidationError('Перечисления не могут быть одинаковыми')

        if enum_1.enum.class_id != enum_2.enum.class_id:
            raise ValidationError('Перечисления должны быть из одного класса')

        enum_1.num, enum_2.num = enum_2.num, enum_1.num

        return cleaned_data
