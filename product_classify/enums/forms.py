from django.forms import (
    ModelChoiceField,
    ModelForm,
    CharField,
    ImageField,
    FloatField,
    IntegerField,
    Form,
)
from django.db import transaction
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

from classes.models import ClassStruct
from classes.constants import EnumsIds

from enums.models import Enums
from enums.constants import EnumsConsts
from enums.errors import *


def validate_positive_int(value):
    if value <= EnumsConsts.INT_VALUE_LOWER_BOUND:
        raise ValidationError(IntEnumErrors.NEGATIVE_VALUE_ERROR)


def validate_positive_double(value):
    if value <= EnumsConsts.DOUBLE_VALUE_LOWER_BOUND:
        raise ValidationError(DoubleEnumErrors.NEGATIVE_VALUE_ERROR)


class EnumsForm(ModelForm):
    enum = ModelChoiceField(
        label="Перечисление",
        queryset=ClassStruct.objects.none(),
        empty_label="Выберите перечисление",
        required=True,
        error_messages={"required": CommonEnumErrors.EMPTY_ENUM_ERROR},
    )
    image = ImageField(
        help_text='Разрешенные форматы изображений: ["jpg", "png"]',
        label="Путь к изображению",
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])],
    )
    name = CharField(
        max_length=EnumsConsts.NAME_MAX_LENGTH,
        label="Название перечисления",
        required=False,
    )
    short_name = CharField(
        max_length=EnumsConsts.SHORT_NAME_MAX_LENGTH,
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

        if parent_id == EnumsIds.STRING:
            if not short_name or not name:
                raise ValidationError(StringEnumErrors.EMPTY_FIELDS_ERROR)
            if any([image, int_value, double_value]):
                raise ValidationError(StringEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)
        elif parent_id == EnumsIds.IMAGE:
            if not image:
                raise ValidationError(ImageEnumErrors.EMPTY_FIELDS_ERROR)
            if any([int_value, double_value]):
                raise ValidationError(ImageEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)
        elif parent_id == EnumsIds.DOUBLE:
            if not double_value:
                raise ValidationError(DoubleEnumErrors.EMPTY_FIELDS_ERROR)
            if any([int_value, image, short_name, name]):
                raise ValidationError(DoubleEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)
        elif parent_id == EnumsIds.INT:
            if not int_value:
                raise ValidationError(IntEnumErrors.EMPTY_FIELDS_ERROR)
            if any([double_value, image, short_name, name]):
                raise ValidationError(IntEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)

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
        
        enum_1: Enums = cleaned_data.get("enum_1", None)
        enum_2: Enums = cleaned_data.get("enum_2", None)

        if not enum_1:
            raise ValidationError(ChangeNumErrors.EMPTY_FIRST_NUM)

        if not enum_2:
            raise ValidationError(ChangeNumErrors.EMPTY_SECOND_NUM)

        if enum_1.pk == enum_2.pk:
            raise ValidationError(ChangeNumErrors.EQUAL_ENUMS)

        if enum_1.enum.pk != enum_2.enum.pk:
            raise ValidationError(ChangeNumErrors.NON_SAME_CLASS)

        with transaction.atomic():        
            old_num_1 = enum_1.num
            old_num_2 = enum_2.num

            temp_num_1 = EnumsConsts.MAX_NUM_VALUE
            temp_num_2 = EnumsConsts.MAX_NUM_VALUE - 1
            enum_1.num = temp_num_1
            enum_2.num = temp_num_2
            enum_1.save(update_fields=['num'])
            enum_2.save(update_fields=['num'])

            enum_1.num = old_num_2
            enum_2.num = old_num_1
            enum_1.save(update_fields=['num'])
            enum_2.save(update_fields=['num'])

        return cleaned_data
