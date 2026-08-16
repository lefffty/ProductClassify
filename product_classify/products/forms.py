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
from products.errors import (
    ProdErrors,
    EnumsParErrors,
    IntParErrors,
    DoubleParErrors,
    CommonParProdErrors
)


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
            "required": CommonParProdErrors.EMPTY_PROD_FIELD,
        }
    )
    par = ModelChoiceField(
        queryset=Parametr.objects.none(),
        label="Параметр",
        required=True,
        error_messages={
            "required": CommonParProdErrors.EMPTY_PAR_FIELD,
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

        # получаем из формы поля изделия и параметра
        prod = cleaned_data.get("prod")
        par = cleaned_data.get("par")

        # если поле для изделия пустое, то выбрасываем исключение
        if not prod:
            return cleaned_data

        # если поле для параметра пустое, то выбрасываем исключение
        if not par:
            return cleaned_data

        # находим идентификатор родительского класса изделия
        cls_id = prod.class_field.id

        # находим все параметры родительского класса изделия
        class_params_ids = ParClass.objects.filter(
            class_field=cls_id,
        ).values_list("parametr", flat=True)

        # проверяем, что параметр входит в число параметров родительского класса
        if par.id not in class_params_ids:
            raise ValidationError(CommonParProdErrors.INVALID_PAR.format(par.name, prod.class_field.name))

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
                # проверяем, указано ли значение поля double_value для целочисленного параметра
                if cleaned_data[double_key]:
                    raise ValidationError(IntParErrors.DOUBLE_FIELD_SPECIFIED)

                # проверяем, указано ли значение поля enum_val для целочисленного параметра
                if cleaned_data["enum_val"]:
                    raise ValidationError(IntParErrors.ENUM_FIELD_SPECIFIED)

                # проверяем, указано ли значение поля int_value для целочисленного параметра
                if not cleaned_data[int_key]:
                    raise ValidationError(IntParErrors.INT_FIELD_EMPTY)

                # если значение целочисленного параметра не входит в заданный диапазон
                if not mn_value <= cleaned_data[int_key] <= mx_value:
                    raise ValidationError(IntParErrors.INVALID_RANGE.format(int(mn_value), int(mx_value)))
                
            # если параметр является вещественным
            else:
                # если для вещественного параметра изделия указано значение поля int_value
                if cleaned_data[int_key]:
                    raise ValidationError(DoubleParErrors.INT_FIELD_SPECIFIED)

                # проверяем, указано ли значение поля enum_val для вещественного параметра
                if cleaned_data["enum_val"]:
                    raise ValidationError(DoubleParErrors.ENUM_FIELD_SPECIFIED)

                # проверяем, указано ли значение поля double_value для вещественного параметра
                if not cleaned_data[double_key]:
                    raise ValidationError(DoubleParErrors.DOUBLE_FIELD_EMPTY)

                # если значение вещественного параметра не входит в заданный диапазон
                if cleaned_data[double_key] < mn_value or cleaned_data[double_key] > mx_value:
                    raise ValidationError(DoubleParErrors.INVALID_RANGE.format(mn_value, mx_value))
                
        # если параметр является параметром-перечислением
        elif par.parametr_type.id in ENUMS_IDS:

            # то проверяем, что в форме не указаны значения int_value или double_value
            int_value = cleaned_data.get("int_value")
            double_value = cleaned_data.get("double_value")
            enum_val = cleaned_data.get("enum_val")

            # проверяем, указано ли значение int_value для параметра-перечисления
            if int_value:
                raise ValidationError(EnumsParErrors.INT_FIELD_SPECIFIED)

            # проверяем, указано ли значение double_value для параметра-перечисления
            if double_value:
                raise ValidationError(EnumsParErrors.DOUBLE_FIELD_SPECIFIED)

            # проверяем, указано ли значение enum_value для параметра-перечисления
            if not enum_val:
                raise ValidationError(EnumsParErrors.ENUM_FIELD_EMPTY)

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
                in ClassStruct.enum_classes().values_list("id", flat=True)
                and ParProd.objects.filter(par=par_class.parametr).exists()
            ):
                self.fields[par_class.parametr.name] = ModelChoiceField(
                    queryset=Enums.objects.filter(
                        parprod__par=par_class.parametr
                    ).distinct(),
                    label=par_class.parametr.name,
                    required=False,
                )
