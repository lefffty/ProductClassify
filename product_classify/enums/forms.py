from django.forms import (
    ModelChoiceField,
    ModelForm,
    CharField,
    ImageField,
    FloatField,
    IntegerField,
    Form,
)
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

from classes.models import ClassStruct

from .models import Enums
from .constants import (
    INT_ENUMS_ID,
    IMAGE_ENUMS_ID,
    DOUBLE_ENUMS_ID,
    STRING_ENUMS_ID,
    ENUMS_FORM_NAME_MAX_LENGTH,
    ENUMS_FORM_SHORT_NAME_MAX_LENGTH,
    ENUMS_FORM_INT_VALUE_LOWER_BOUND,
    ENUMS_FORM_DOUBLE_VALUE_LOWER_BOUND,
)


def validate_positive_int(value):
    if value <= ENUMS_FORM_INT_VALUE_LOWER_BOUND:
        raise ValidationError("Значение должно быть положительным числом (> 0)")


def validate_positive_double(value):
    if value <= ENUMS_FORM_DOUBLE_VALUE_LOWER_BOUND:
        raise ValidationError("Значение должно быть положительным числом (> 0)")


class EnumsForm(ModelForm):
    enum = ModelChoiceField(
        label="Перечисление",
        queryset=ClassStruct.objects.none(),
        empty_label="Выберите перечисление",
        required=True,
        error_messages={"required": "Поле перечисления необходимо заполнить"},
    )
    image = ImageField(
        help_text='Разрешенные форматы изображений: ["jpg", "png"]',
        label="Путь к изображению",
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])],
    )
    name = CharField(
        max_length=ENUMS_FORM_NAME_MAX_LENGTH,
        label="Название перечисления",
        required=False,
    )
    short_name = CharField(
        max_length=ENUMS_FORM_SHORT_NAME_MAX_LENGTH,
        required=False,
        label="Сокращенное название перечисления",
    )
    double_value = FloatField(
        required=False,
        label="Вещественное значение перечисления",
        validators=[validate_positive_double],
    )
    int_value = IntegerField(
        required=False,
        label="Целочисленное значение перечисления",
        validators=[validate_positive_int],
    )

    class Meta:
        model = Enums
        fields = (
            "enum",
            "name",
            "short_name",
            "double_value",
            "int_value",
            "image",
        )
        labels = {
            "enum": "Родитель перечисления",
            "name": "Название перечисления",
            "short_name": "Сокращенное название перечисления",
            "double_value": "Вещественное значение перечисления",
            "int_value": "Целочисленное значение перечисления",
            "image": "Путь к изображению",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["enum"].queryset = ClassStruct.terminal_enum_classes()

    def clean(self):
        cleaned_data = super().clean()
        enum = cleaned_data.get("enum")

        if not enum:
            return cleaned_data

        image = cleaned_data.get("image")
        int_value = cleaned_data.get("int_value")
        double_value = cleaned_data.get("double_value")
        name = cleaned_data.get("name")
        short_name = cleaned_data.get("short_name")

        parent_id = enum.main_class.id

        if parent_id == STRING_ENUMS_ID:
            if not short_name or not name:
                raise ValidationError(
                    "Для строкового перечисления поля 'Название' и 'Сокращенное название' обязательны для заполнения."
                )
            if any([image, int_value, double_value]):
                raise ValidationError("""
                    Значение перечисления строк не должно иметь пути к изображению, целочисленного и вещественного
                    значений
                """)
        elif parent_id == IMAGE_ENUMS_ID:
            if not image:
                raise ValidationError("""
                    Для перечисления изображений необходимо загрузить изображение (поле 'Путь к изображению').
                """)
            if any([int_value, double_value]):
                raise ValidationError("""Значение перечисления изображений не должно
                        иметь численных значений""")
        elif parent_id == DOUBLE_ENUMS_ID:
            if not double_value:
                raise ValidationError(
                    "Для вещественного перечисления необходимо указать вещественное значение "
                    "(поле 'Вещественное значение перечисления')."
                )
            if any([int_value, image, short_name, name]):
                raise ValidationError("""Вещественное перечисление не должно иметь
                    целочисленного значения и путь к изображению""")
        elif parent_id == INT_ENUMS_ID:
            if not int_value:
                raise ValidationError(
                    "Для целочисленного перечисления необходимо указать целочисленное значение "
                    "(поле 'Целочисленное значение перечисления')."
                )
            if any([double_value, image, short_name, name]):
                raise ValidationError("""Целочисленное перечисление не должно иметь
                    вещественного значения и путь к изображению""")

        if not self.instance.pk:
            cleaned_data["num"] = Enums.objects.filter(enum=enum).count() + 1
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.num = self.cleaned_data.get("num", 1)
        if commit:
            instance.save()
        return instance


class ChangeNumForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["enum_1"] = ModelChoiceField(
            queryset=Enums.objects.all(),
            empty_label="Выберите перечисление",
            required=True,
            label="Перечисление 1",
        )
        self.fields["enum_2"] = ModelChoiceField(
            queryset=Enums.objects.all(),
            empty_label="Выберите перечисление",
            required=True,
            label="Перечисление 2",
        )

    def clean(self):
        cleaned_data = super().clean()
        enum_1 = cleaned_data.get("enum_1", None)
        enum_2 = cleaned_data.get("enum_2", None)

        if not enum_1:
            raise ValidationError(
                "Пожалуйста, выберите первое перечисление."
            )

        if not enum_2:
            raise ValidationError(
                "Пожалуйста, выберите второе перечисление."
            )

        if enum_1 == enum_2:
            raise ValidationError("Перечисления не могут быть одинаковыми")

        if enum_1.enum.pk != enum_2.enum.pk:
            raise ValidationError("Перечисления должны быть из одного класса")

        enum_1.num, enum_2.num = enum_2.num, enum_1.num

        return cleaned_data
