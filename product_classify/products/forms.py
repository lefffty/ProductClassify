from django.forms import (
    ModelChoiceField,
    IntegerField,
    FloatField,
    ImageField,
    ModelForm,
    CharField,
    Field,
    Form,
)
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

from classes.models import ClassStruct, ParClass
from classes.constants import ParamIds, ENUMS_IDS
from enums.models import Enums

from products.models import Parametr, ParProd, Prod
from products.constants import ProdConsts
from products.errors import *


class ProdForm(ModelForm):
    class_field = ModelChoiceField(
        label="Родительский класс",
        queryset=ClassStruct.objects.none(),
        required=True,
        error_messages={
            "required": ProdErrors.EMPTY_CLASS_FIELD
        },
    )
    name = CharField(
        label="Название изделия",
        max_length=ProdConsts.NAME_MAX_LENGTH,
        required=True,
        error_messages={
            "required": ProdErrors.EMPTY_NAME_FIELD
        },
    )
    short_name = CharField(
        label="Сокращенное название изделия",
        max_length=ProdConsts.SHORT_NAME_MAX_LENGTH,
        required=False,
    )
    image = ImageField(
        label="Изображение изделия",
        required=False,
        validators=[FileExtensionValidator(["jpg", "png"])],
    )

    class Meta:
        model = Prod
        fields = (
            "name",
            "short_name",
            "class_field",
            "image",
        )
        labels = {
            "name": "Название изделия",
            "short_name": "Сокращенное название изделия",
            "class_field": "Родительский класс",
            "image": "Изображение изделия",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["class_field"].queryset = ClassStruct.products().order_by("name")


class ParProdForm(ModelForm):
    prod = ModelChoiceField(
        queryset=Prod.objects.none(),
        label="Изделие",
        required=True,
        error_messages={
            "required": "Поле для изделия необходимо заполнить",
        }
    )
    par = ModelChoiceField(
        queryset=Parametr.objects.none(),
        label="Параметр",
        required=True,
        error_messages={
            "required": "Поле для параметра необходимо заполнить",
        }
    )
    enum_val = ModelChoiceField(
        queryset=Enums.objects.none(),
        label="Значение перечисления",
        required=False,
    )
    int_value = IntegerField(
        label="Целочисленное значение параметра",
        required=False,
    )
    double_value = FloatField(
        label="Вещественное значение параметра",
        required=False,
    )

    class Meta:
        model = ParProd
        fields = (
            "prod",
            "par",
            "int_value",
            "double_value",
            "enum_val",
        )
        labels = {
            "prod": "Изделие",
            "par": "Параметр",
            "int_value": "Целочисленное значение параметра",
            "double_value": "Вещественное значение параметра",
            "enum_val": "Значение параметра-перечисления",
        }

    def __init__(self, *args, **kwargs):
        prod_id = kwargs.pop("prod_id", None)
        super().__init__(*args, **kwargs)
        self.fields["par"].queryset = Parametr.parameters()
        self.fields["enum_val"].queryset = Enums.objects.all()
        if prod_id:
            self.fields["prod"].initial = Prod.objects.get(pk=prod_id)
        else:
            self.fields["prod"].queryset = Prod.objects.all()

    def clean(self):
        cleaned_data = super().clean()

        # вытаскиваем из формы изделие и параметр
        prod = cleaned_data.get("prod")
        par = cleaned_data.get("par")

        # если поле для изделия пустое 
        if not prod:
            raise ValidationError(
                "Поле для изделия необходимо заполнить"
            )

        # если поле для параметра пустое
        if not par:
            raise ValidationError(
                "Поле для параметра необходимо заполнить"
            )

        # находим идентификатор родительского класса изделия
        cls_id = prod.class_field.id

        # находим все параметры родительского класса изделия
        class_params_ids = ParClass.objects.filter(
            class_field=cls_id,
        ).values_list("parametr", flat=True)

        # проверяем, что параметр входит в число параметров родительского класса
        if par.id not in class_params_ids:
            raise ValidationError(
                "Параметр '{}' не принадлежит классу изделия '{}'".format(
                    par.name, prod.class_field.name
                )
            )

        # отыскиваем параметр класса в таблице ParClass
        par_class = ParClass.objects.get(
            class_field=cls_id,
            parametr=par,
        )

        # проверяем, что если параметр является численным
        if par.parametr_type.id in [ParamIds.DOUBLE, ParamIds.INT]:
            # получаем максимальное и минимальное значения параметра
            mn_value, mx_value = par_class.min_value, par_class.max_value

            int_key = "int_value"
            double_key = "double_value"

            # если параметр является целочисленным
            if par.parametr_type.id == ParamIds.INT:
                # если для целочисленного параметра изделия указано значение поля double_value
                if cleaned_data[double_key]:
                    raise ValidationError(
                        "Для целочисленного параметра нельзя указать значение поля double_value"
                    )

                if cleaned_data["enum_val"]:
                    raise ValidationError(
                        "Для целочисленного параметра нельзя указать значение поля enum_val"
                    )

                if not cleaned_data[int_key]:
                    raise ValidationError(
                        "Для целочисленного параметра изделия необходимо указать значение поля int_value"
                    )

                # если значение целочисленного параметра не входит в заданный диапазон
                if cleaned_data[int_key] < mn_value or cleaned_data[int_key] > mx_value:
                    raise ValidationError(
                        f"Целочисленное значение не входит в границы диапазона(<{mn_value}, {mx_value}>)"
                    )
            # если параметр является вещественным
            else:
                # если для вещественного параметра изделия указано значение поля int_value
                if cleaned_data[int_key]:
                    raise ValidationError(
                        "Для вещественного параметра нельзя указать значение поля int_value"
                    )

                if cleaned_data["enum_val"]:
                    raise ValidationError(
                        "Для вещественного параметра нельзя указать значение поля enum_val"
                    )

                if not cleaned_data[double_key]:
                    raise ValidationError(
                        "Для вещественного параметра изделия необходимо указать значение поля int_value"
                    )

                # если значение вещественного параметра не входит в заданный диапазон
                if cleaned_data[double_key] < mn_value or cleaned_data[double_key] > mx_value:
                    raise ValidationError(
                        f"Вещественное значение не входит в границы диапазона(<{mn_value}, {mx_value}>)"
                    )
        # если параметр является параметром-перечислением
        elif par.parametr_type.id in ENUMS_IDS:
            # то проверяем, что в форме не указаны значения int_value или double_value
            int_value = cleaned_data.get("int_value")
            double_value = cleaned_data.get("double_value")

            # проверяем, указано ли значение int_value для параметра-перечисления
            if int_value:
                raise ValidationError(
                    "Для параметра-перечисления изделия нельзя указать значение поля int_value"
                )

            # проверяем, указано ли значение double_value для параметра-перечисления
            if double_value:
                raise ValidationError(
                    "Для параметра-перечисления изделия нельзя указать значение поля double_value"
                )

            if not cleaned_data["enum_val"]:
                raise ValidationError(
                    "Для параметра-перечисления изделия необходимо указать значение поля enum_val"
                )

        return cleaned_data


class RangeField(Field):
    def to_python(self, value):
        if not value:
            return None
        try:
            start, end = value.split("-")
            return start, end
        except ValueError:
            raise ValidationError("Некорректный формат диапазона")


class SearchForm(Form):
    def __init__(self, *args, **kwargs):
        cls = kwargs.pop("cls", None)
        super().__init__(*args, **kwargs)

        for par_class in ParClass.objects.filter(class_field=cls):
            if (
                par_class.parametr.parametr_type.id == ParamIds.INT
                and ParProd.objects.filter(par=par_class.parametr).exists()
            ):
                self.fields[f"{par_class.parametr.name}"] = RangeField(
                    label=f"{par_class.parametr.name}",
                    required=False,
                    help_text=f"""Вводить в формате "min-max" (например, "10.0-20.0").
                            <br>Границы диапазоны: {par_class.min_value}-{par_class.max_value}""",
                )
            elif (
                par_class.parametr.parametr_type.id
                in ClassStruct.enum_classes.all().values_list("id", flat=True)
                and ParProd.objects.filter(par=par_class.parametr).exists()
            ):
                self.fields[par_class.parametr.name] = ModelChoiceField(
                    queryset=Enums.objects.filter(
                        parprod__par=par_class.parametr
                    ).distinct(),
                    label=par_class.parametr.name,
                    required=False,
                )
