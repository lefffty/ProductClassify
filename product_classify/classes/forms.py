from django.forms import (
    ModelForm,
    ModelChoiceField,
    FloatField,
    CharField,
    Form,
)
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import connection

from ei.models import Ei
from parametr.models import Parametr

from .models import (
    ClassStruct,
    ParClass,
)
from .constants import (
    NUM_PARAM_ID,
    PROD_CLASS_FORM_MAX_LENGTH,
    ENUM_CLASS_FORM_NAME_MAX_LENGTH,
    PARCLASS_FORM_MAX_VALUE_LOWER_BOUND,
    PARCLASS_FORM_MIN_VALUE_LOWER_BOUND,
    PROD_CLASS_FORM_SHORT_NAME_MAX_LENGTH,
    ENUM_CLASS_FORM_SHORT_NAME_MAX_LENGTH,
)
from .constants import (
    CLASSIFICATOR_CYCLE_ERROR,
    EMPTY_MAIN_CLASS_ERROR,
    EMPTY_NAME_ERROR,
)


class ProdClassForm(ModelForm):
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
            "required": EMPTY_MAIN_CLASS_ERROR,
        },
    )
    name = CharField(
        max_length=PROD_CLASS_FORM_MAX_LENGTH,
        required=True,
        label="Название класса",
        error_messages={
            "required": EMPTY_NAME_ERROR,
        },
    )
    short_name = CharField(
        max_length=PROD_CLASS_FORM_SHORT_NAME_MAX_LENGTH,
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

    def _check_class_struct_cycles(self, cursor: object, cls_id: int, main_cls_id: int):
        cursor.execute(
            "SELECT * FROM check_class_struct_cycles(%s, %s);",
            [cls_id, main_cls_id],
        )
        is_cycle = cursor.fetchone()[0]
        return is_cycle

    def clean(self):
        if "main_class" not in self.cleaned_data:
            return super().clean()

        if self.instance.pk:
            with connection.cursor() as cursor:
                self.instance.save()
                cls_id = self.instance.pk
                main_cls_id = self.cleaned_data["main_class"].id
                is_cycle = self._check_class_struct_cycles(cursor, cls_id, main_cls_id)
                if is_cycle:
                    raise ValidationError(
                        CLASSIFICATOR_CYCLE_ERROR
                    )
                return super().clean()
        else:
            return super().clean()


class EnumClassForm(ModelForm):
    main_class = ModelChoiceField(
        label="Родительский класс",
        queryset=ClassStruct.objects.none(),
        empty_label="Выберите родительский класс",
        required=True,
        error_messages={
            "required": EMPTY_MAIN_CLASS_ERROR
        },
    )
    name = CharField(
        max_length=ENUM_CLASS_FORM_NAME_MAX_LENGTH,
        required=True,
        label="Название класса",
        error_messages={"required": EMPTY_NAME_ERROR}
    )
    short_name = CharField(
        max_length=ENUM_CLASS_FORM_SHORT_NAME_MAX_LENGTH,
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

    def _check_class_struct_cycles(self, cursor: object, cls_id: int, main_cls_id: int):
        cursor.execute(
            "SELECT * FROM check_class_struct_cycles(%s, %s);",
            [cls_id, main_cls_id],
        )
        is_cycle = cursor.fetchone()[0]
        return is_cycle

    def clean(self):
        if "main_class" not in self.cleaned_data:
            return super().clean()

        if self.instance.pk:
            with connection.cursor() as cursor:
                self.instance.save()
                cls_id = self.instance.pk
                main_cls_id = self.cleaned_data["main_class"].id
                is_cycle = self._check_class_struct_cycles(cursor, cls_id, main_cls_id)
                if is_cycle:
                    raise ValidationError(CLASSIFICATOR_CYCLE_ERROR)
                return super().clean()
        else:
            return super().clean()


class ParClassForm(ModelForm):
    class_field = ModelChoiceField(
        label="Класс изделия",
        queryset=ClassStruct.objects.none(),
        required=True,
    )
    parametr = ModelChoiceField(
        label="Параметр",
        queryset=Parametr.objects.none(),
        required=True,
    )
    min_value = FloatField(
        label="Минимальное значение параметра класса",
        validators=[
            MinValueValidator(PARCLASS_FORM_MIN_VALUE_LOWER_BOUND),
        ],
        required=False,
    )
    max_value = FloatField(
        label="Максимальное значение параметра класса",
        validators=[
            MinValueValidator(PARCLASS_FORM_MAX_VALUE_LOWER_BOUND),
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
        parametr = cleaned_data.get("parametr")

        if not class_field:
            raise ValidationError("Поле 'Класс изделия' обязательно для заполнения.")
        if not parametr:
            raise ValidationError("Поле 'Параметр' обязательно для заполнения.")

        param_tp = parametr.parametr_type.id
        min_val = cleaned_data.get("min_value")
        max_val = cleaned_data.get("max_value")

        if param_tp in ClassStruct.enum_classes().values_list("id", flat=True) and (
            min_val is not None or max_val is not None
        ):
            raise ValidationError(
                "У параметра-перечисления не должно быть максимального и минимального значений!"
            )
        elif param_tp in ClassStruct.objects.filter(
            main_class__exact=NUM_PARAM_ID
        ).values_list("id", flat=True) and (min_val and max_val and min_val > max_val):
            raise ValidationError(
                "У численного параметра минимальное значение должно быть меньше максимального!"
            )

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
        if not class_field_1:
            raise ValidationError("Поле class_field_1 не может быть пустым")
        class_field_2 = cleaned_data.get("class_field_2")
        if not class_field_2:
            raise ValidationError("Поле class_field_2 не может быть пустым")
        if class_field_1 == class_field_2:
            raise ValidationError("Классы изделия не могут быть одинаковыми!")
        return cleaned_data
