from django.forms import (
    ModelForm,
    ModelChoiceField,
    Form,
    Field,
)
from django.core.exceptions import ValidationError

from product_classify.enums.models import Enums
from product_classify.classes.models import ClassStruct, ParClass

from .models import Parametr, ParProd, Prod
from .constants import (
    INT_PARAMS,
    FLOAT_PARAMS,
)


class ProdForm(ModelForm):
    class_field = ModelChoiceField(
        label="Родительский класс",
        queryset=ClassStruct.products.all().order_by("name"),
    )

    class Meta:
        model = Prod
        fields = (
            "name",
            "short_name",
            "class_field",
        )
        labels = {
            "name": "Название изделия",
            "short_name": "Сокращенное название изделия",
            "class_field": "Родительский класс",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["class_field"].queryset = ClassStruct.products.all().order_by(
            "name"
        )


class ParProdForm(ModelForm):
    prod = ModelChoiceField(
        queryset=Prod.objects.all(),
        label="Изделие",
    )
    par = ModelChoiceField(
        queryset=Parametr.parameters.all(),
        label="Параметр",
    )
    enum_val = ModelChoiceField(
        queryset=Enums.objects.all(),
        label="Значение перечисления",
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
        self.fields["par"].queryset = Parametr.parameters.all()
        self.fields["enum_val"].queryset = Enums.objects.all()
        if prod_id:
            self.fields["prod"].initial = Prod.objects.get(prod_id=prod_id)

    def clean(self):
        cleaned_data = super().clean()

        prod = cleaned_data.get("prod")
        par = cleaned_data.get("par")

        cls_id = prod.class_field.id
        class_params_ids = ParClass.objects.filter(
            class_field=cls_id,
        ).values_list("parametr", flat=True)
        if par.id not in class_params_ids:
            raise ValidationError("У класса изделия нет таких параметров!")
        par_class = ParClass.objects.get(
            class_field=cls_id,
            parametr=par,
        )
        mn_value = par_class.min_value
        mx_value = par_class.max_value
        if par.parametr_type.id == FLOAT_PARAMS:
            cleaned_data["double_value"] = None
            cleaned_data["enum_val"] = None
            if (
                cleaned_data["int_value"] < mn_value
                or cleaned_data["int_value"] > mx_value
            ):
                raise ValidationError(
                    "Целочисленное значение не входит в границы диапазона"
                )
        elif par.parametr_type.id == INT_PARAMS:
            cleaned_data["int_value"] = None
            cleaned_data["enum_val"] = None
            if (
                cleaned_data["double_value"] < mn_value
                or cleaned_data["double_value"] > mx_value
            ):
                raise ValidationError(
                    "Вещественное значение не входит в границы диапазона"
                )
        else:
            cleaned_data["int_value"] = None
            cleaned_data["double_value"] = None

        return cleaned_data


class RangeField(Field):
    def to_python(self, value):
        if not value:
            return None
        try:
            start, end = value.split("-")
            return (start, end)
        except ValueError:
            raise ValidationError("Некорректный формат диапазона")


class SearchForm(Form):
    def __init__(self, *args, **kwargs):
        cls = kwargs.pop("cls", None)
        super().__init__(*args, **kwargs)

        for par_class in ParClass.objects.filter(class_field=cls):
            if (
                par_class.parametr.parametr_type.id == INT_PARAMS
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
