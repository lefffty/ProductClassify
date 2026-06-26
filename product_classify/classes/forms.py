from django.forms import (
    ModelForm,
    ModelChoiceField,
    FloatField,
    CharField,
    Form,
)
from django.core.exceptions import ValidationError
from django.db import connection

from ei.models import Ei
from parametr.models import Parametr

from .models import (
    ClassStruct,
    ParClass,
)
from .validators import positive_validate
from .constants import (
    PROD_CLASS_FORM_MAX_LENGTH,
    ENUM_CLASS_FORM_NAME_MAX_LENGTH,
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
    )
    name = CharField(
        max_length=PROD_CLASS_FORM_MAX_LENGTH,
        required=True,
        label="Название класса",
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
        with connection.cursor() as cursor:
            self.instance.save()
            class_id = self.instance.pk
            main_class_id = self.cleaned_data["main_class"].id
            cursor.execute(f"""SELECT * FROM check_class_struct_cycles(
                    {class_id},
                    {main_class_id}
                );""")
            is_cycle = cursor.fetchone()[0]
            if is_cycle:
                raise ValidationError("""При изменении класса в классификаторе
                    образовывается цикл!""")
        return super().clean()


class EnumClassForm(ModelForm):
    main_class = ModelChoiceField(
        label="Родительский класс",
        queryset=ClassStruct.objects.none(),
        empty_label="Выберите родительский класс",
    )
    name = CharField(
        max_length=ENUM_CLASS_FORM_NAME_MAX_LENGTH,
        required=True,
        label="Название класса",
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
        with connection.cursor() as cursor:
            self.instance.save()
            class_id = self.instance.pk
            main_class_id = self.cleaned_data["main_class"].id
            cursor.execute(f"""SELECT * FROM check_class_struct_cycles(
                    {class_id},
                    {main_class_id}
                );""")
            is_cycle = cursor.fetchone()[0]
            if is_cycle:
                raise ValidationError("""При изменении класса в классификаторе
                    образовывается цикл!""")
        return super().clean()


class ParClassForm(ModelForm):
    class_field = ModelChoiceField(
        label="Класс изделия",
        queryset=ClassStruct.objects.none(),
    )
    parametr = ModelChoiceField(
        label="Параметр",
        queryset=Parametr.objects.none(),
    )
    min_value = FloatField(
        label="Минимальное значение параметра класса",
        validators=[
            positive_validate,
        ],
        required=False,
    )
    max_value = FloatField(
        label="Максимальное значение параметра класса",
        validators=[
            positive_validate,
        ],
        required=False,
    )

    class Meta:
        model = ParClass
        fields = (
            "class_field",
            "parametr",
            "min_value",
            "max_value",
        )
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

        param = cleaned_data["parametr"]
        min_val = cleaned_data["min_value"]
        max_val = cleaned_data["max_value"]
        param_tp = param.parametr_type.id
        cls_id = cleaned_data["class_field"].id

        if param_tp in ClassStruct.enum_classes.values_list("id", flat=True) and (
            min_val or max_val
        ):
            raise ValidationError("""У параметра-перечисления не должно быть
                максимального и минимального значений!""")

        with connection.cursor() as cursor:
            if param.parametr_type.id in [15, 16, 18, 19]:
                cursor.execute(
                    """SELECT * FROM to_add_parametr_to_class(
                        %s, %s, %s, %s
                    ); """,
                    [cls_id, param.pk, None, None],
                )
            else:
                cursor.execute(
                    """SELECT * FROM to_add_parametr_to_class(
                        %s, %s, %s, %s
                    );""",
                    [cls_id, param.pk, min_val, max_val],
                )
        return cleaned_data


class ChangeParclassNumForm(Form):
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
        class_field_1 = cleaned_data["class_field_1"]
        class_field_2 = cleaned_data["class_field_2"]
        if class_field_1 == class_field_2:
            raise ValidationError("Классы изделия не могут быть одинаковыми!")
        return cleaned_data
