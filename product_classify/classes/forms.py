from django.forms import (
    ModelForm,
    ModelChoiceField,
    FloatField,
    CharField,
    Form,
)
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from ei.models import Ei
from parametr.models import Parametr

from classes.models import ClassStruct, ParClass
from classes.constants import ProdClassConsts, ParClassConsts, EnumClassConsts, EnumsIds, ParamIds, NUMERIC_PARAMS, ENUM_PARAMS
from classes.errors import ClassStructErrors, ParClassErrors, ChangeParClassErrors


class ProdClassForm(ModelForm):
    """Форма для создания класса изделия
    """
    base_ei = ModelChoiceField(
        label="Единица измерения",
        empty_label="Выберите единицу измерения",
        required=False,
        queryset=Ei.objects.none(),
    )
    main_class = ModelChoiceField(
        label="Родительский класс",
        empty_label="Выберите родительский класс",
        queryset=ClassStruct.objects.none(),
        required=True,
        error_messages={
            "required": ClassStructErrors.EMPTY_MAIN_CLASS_ERROR,
        },
    )
    name = CharField(
        max_length=ProdClassConsts.NAME_MAX_LENGTH,
        required=True,
        label="Название класса",
        error_messages={
            "required": ClassStructErrors.EMPTY_NAME_ERROR,
        },
    )
    short_name = CharField(
        max_length=ProdClassConsts.SHORT_NAME_MAX_LENGTH,
        required=False,
        label="Сокращенное название класса",
    )

    class Meta:
        model = ClassStruct
        fields = ("name", "short_name", "base_ei", "main_class")
        labels = {
            "name": "Название класса",
            "short_name": "Сокращенное название класса",
            "base_ei": "Единица измерения класса",
            "main_class": "Родитель класса",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["main_class"].queryset = ClassStruct.terminal_product_classes()
        self.fields["base_ei"].queryset = Ei.objects.all()

    def clean(self):
        # проверяем, что поле main_class заполнено
        if "main_class" not in self.cleaned_data:
            return super().clean()

        # если форма предназначена для редактирования существующего объекта
        if self.instance.pk:
            self.instance.save()
            cls_id = self.instance.pk
            main_cls_id = self.cleaned_data["main_class"].id
            # проверяем, что при редактирования объекта в классификаторе не образовался цикл
            is_cycle = ClassStruct.check_class_struct_cycles(cls_id, main_cls_id)
            # выбрасываем исключение, если образовался цикл
            if is_cycle:
                raise ValidationError(
                    ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR
                )
            return super().clean()
        else:
            return super().clean()


class EnumClassForm(ModelForm):
    """Форма для создания класса перечисления
    """
    main_class = ModelChoiceField(
        label="Родительский класс",
        queryset=ClassStruct.objects.none(),
        empty_label="Выберите родительский класс",
        required=True,
        error_messages={
            "required": ClassStructErrors.EMPTY_MAIN_CLASS_ERROR
        },
    )
    name = CharField(
        max_length=EnumClassConsts.NAME_MAX_LENGTH,
        required=True,
        label="Название класса",
        error_messages={"required": ClassStructErrors.EMPTY_NAME_ERROR}
    )
    short_name = CharField(
        max_length=EnumClassConsts.SHORT_NAME_MAX_LENGTH,
        required=False,
        label="Сокращенное название класса",
    )

    class Meta:
        model = ClassStruct
        fields = ("name", "short_name", "main_class")
        labels = {
            "name": "Название класса",
            "short_name": "Сокращенное название класса",
            "main_class": "Родитель класса",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["main_class"].queryset = ClassStruct.all_enum_classes()

    def clean(self):
        # проверяем, что поле main_class заполнено
        if "main_class" not in self.cleaned_data:
            return super().clean()

        # если форма предназначена для редактирования существующего объекта
        if self.instance.pk:
            self.instance.save()
            cls_id = self.instance.pk
            main_cls_id = self.cleaned_data["main_class"].id
            # проверяем, что при редактирования объекта в классификаторе не образовался цикл
            is_cycle = ClassStruct.check_class_struct_cycles(cls_id, main_cls_id)
            # выбрасываем исключение, если образовался цикл
            if is_cycle:
                raise ValidationError(ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR)
            return super().clean()
        else:
            return super().clean()


class ParClassForm(ModelForm):
    """Форма для создания параметра класса
    """
    class_field = ModelChoiceField(
        label="Класс изделия",
        queryset=ClassStruct.objects.none(),
        required=True,
        error_messages={
            "required": ParClassErrors.EMPTY_CLASS_FIELD
        }
    )
    parametr = ModelChoiceField(
        label="Параметр",
        queryset=Parametr.objects.none(),
        required=True,
        error_messages={
            "required": ParClassErrors.EMPTY_PAR_FIELD
        }
    )
    min_value = FloatField(
        label="Минимальное значение параметра класса",
        validators=[
            MinValueValidator(ParClassConsts.MIN_VALUE_LOWER_BOUND),
        ],
        required=False,
    )
    max_value = FloatField(
        label="Максимальное значение параметра класса",
        validators=[
            MinValueValidator(ParClassConsts.MAX_VALUE_LOWER_BOUND),
        ],
        required=False,
    )

    class Meta:
        model = ParClass
        fields = ("class_field", "parametr", "min_value", "max_value")
        labels = {
            "class_field": "Класс изделия",
            "parametr": "Параметр",
            "min_value": "Минимальное значение параметра",
            "max_value": "Максимальное значение параметра",
        }

    def __init__(self, *args, **kwargs):
        class_field = kwargs.pop("class_field", None)
        super().__init__(*args, **kwargs)
        self.fields["parametr"].queryset = Parametr.parameters().order_by("id")
        self.fields["class_field"].queryset = ClassStruct.products()
        self.fields["class_field"].initial = class_field

    def clean(self):
        cleaned_data = super().clean()
        class_field = cleaned_data.get("class_field")

        # проверяем, что поле class_field заполнено
        if not class_field:
            return cleaned_data

        parametr = cleaned_data.get("parametr")

        # проверяем, что поле parametr заполнено
        if not parametr:
            return cleaned_data

        param_tp = parametr.parametr_type.pk

        min_val = cleaned_data.get("min_value")
        max_val = cleaned_data.get("max_value")

        # если параметр является перечислением и значения max_value или min_value не None,
        # то выбрасываем исключение с сообщением об этой ошибке 
        if param_tp in ENUM_PARAMS:
            if min_val or max_val:
                raise ValidationError(ParClassErrors.ENUM_AGGREGATE_RANGE_ERROR.format(parametr.name))
        # если параметр является численным и минимальное значение больше максимального значения параметра,
        # то выбрасываем исключение с сообщением об этой ошибке
        elif param_tp in NUMERIC_PARAMS:
            if min_val and max_val and min_val > max_val:
                raise ValidationError(ParClassErrors.MIN_GE_MAX)
        else:
            raise ValidationError(ParClassErrors.AGREGAT_PAR_TYPE)

        # проверяем, что редактируем объект и задаем значение поля num
        if not self.instance.pk:
            cleaned_data["num"] = (
                ParClass.objects.filter(class_field=class_field).count() + 1
            )
        elif self.instance.pk and self.instance.class_field != class_field:
            cleaned_data["num"] = (
                ParClass.objects.filter(class_field=class_field).count() + 1
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if "num" in self.cleaned_data:
            instance.num = self.cleaned_data["num"]
        if commit:
            instance.save()
        return instance


class ChangeParClassNumForm(Form):
    """Форма для изменения позиции параметра класса
    """
    def __init__(self, *args, **kwargs):
        class_id = kwargs.pop("class_id", None)
        super().__init__(*args, **kwargs)
        self.fields["class_field_1"] = ModelChoiceField(
            queryset=ParClass.objects.filter(class_field__id=class_id),
            label="Класс изделия 1",
        )
        self.fields["class_field_2"] = ModelChoiceField(
            queryset=ParClass.objects.filter(class_field__id=class_id),
            label="Класс изделия 2",
        )

    def clean(self):
        cleaned_data = super().clean()
        class_field_1 = cleaned_data.get("class_field_1")

        # проверяем, что поле для первого параметра класса заполнено
        if not class_field_1:
            raise ValidationError(ChangeParClassErrors.EMPTY_FIRST_PAR)

        # проверяем, что поле для второго параметра класса заполнено
        class_field_2 = cleaned_data.get("class_field_2")
        if not class_field_2:
            raise ValidationError(ChangeParClassErrors.EMPTY_SECOND_PAR)

        # проверяем, что оба параметра относятся к одному классу
        if class_field_1 == class_field_2:
            raise ValidationError(ChangeParClassErrors.EQUAL_PAR)
        
        return cleaned_data
