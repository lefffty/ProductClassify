from django.forms import (
    Select,
    TextInput,
    ModelForm,
    CharField,
    NumberInput,
    IntegerField,
    DecimalField,
    ModelChoiceField,
)
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from classes.models import ClassStruct
from products.models import Prod

from route_tech.models import (
    GroupWorkingCenter,
    EconomicActivitySubject,
)
from route_tech.models import ProdOperation, ProdOperationPos
from route_tech.errors import (
    GWCErrors,
    EASErrors,
    ProdOperErrors,
    ProdOperationPosErrors,
)
from route_tech.constants import (
    EASConsts,
    GWCConsts,
    ProdOperationPosConsts,
)


class EconomicActivitySubjectForm(ModelForm):
    name = CharField(
        label="Название субъекта экономической деятельности",
        max_length=EASConsts.NAME_MAX_LENGTH,
        required=True,
        error_messages={
            "required": EASErrors.EMPTY_NAME,
        },
    )
    short_name = CharField(
        label="Сокращенное название субъекта экономической деятельности",
        max_length=EASConsts.SHORT_NAME_MAX_LENGTH,
        required=True,
        error_messages={
            "required": EASErrors.EMPTY_SHORT_NAME,
        },
    )
    main_class = ModelChoiceField(
        label="Ссылка на класса субъекта экономической деятельности",
        queryset=ClassStruct.objects.none(),
        required=True,
        error_messages={
            "required": EASErrors.EMPTY_MAIN_CLASS,
        },
    )
    main_subject = ModelChoiceField(
        label="Родительский субъект экономичекой деятельности",
        queryset=EconomicActivitySubject.objects.none(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["main_class"].queryset = ClassStruct.economic_activity_subjects()
        self.fields["main_subject"].queryset = EconomicActivitySubject.objects.all()

    class Meta:
        model = EconomicActivitySubject
        fields = (
            "name",
            "short_name",
            "main_class",
            "main_subject",
        )


class GroupWorkingCenterForm(ModelForm):
    place = IntegerField(
        label="Количество рабочих мест",
        help_text="Целое положительное число",
        required=True,
        validators=[MinValueValidator(GWCConsts.MIN_PLACE)],
        widget=NumberInput(attrs={"class": "form-control", "min": GWCConsts.MIN_PLACE}),
        error_messages={
            "required": GWCErrors.EMPTY_PLACE,
            "min_value": GWCErrors.INVALID_PLACE,
        },
    )

    class Meta:
        model = GroupWorkingCenter
        fields = ["name", "short_name", "main_class", "eas", "place"]
        labels = {
            "name": "Название группового рабочего центра",
            "short_name": "Сокращённое название",
            "main_class": "Родительский класс",
            "eas": "Субъект экономической деятельности",
        }
        help_texts = {
            "name": "Максимальная длина — {} символов".format(
                GroupWorkingCenter._meta.get_field("name").max_length
            ),
            "short_name": "Максимальная длина — {} символов".format(
                GroupWorkingCenter._meta.get_field("short_name").max_length
            ),
        }
        widgets = {
            "name": TextInput(attrs={"class": "form-control"}),
            "short_name": TextInput(attrs={"class": "form-control"}),
            "main_class": Select(attrs={"class": "form-control"}),
            "eas": Select(attrs={"class": "form-control"}),
        }
        error_messages = {
            "name": {
                "required": GWCErrors.EMPTY_NAME,
            },
            "short_name": {
                "required": GWCErrors.EMPTY_SHORT_NAME,
            },
            "main_class": {
                "required": GWCErrors.EMPTY_MAIN_CLASS,
            },
            "eas": {
                "required": GWCErrors.EMPTY_EAS,
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["main_class"].queryset = ClassStruct.means_of_labor()
        self.fields["eas"].queryset = EconomicActivitySubject.objects.all()


class ProdOperationForm(ModelForm):
    num_of_workers = IntegerField(
        required=True,
        min_value=1,
        widget=NumberInput(attrs={"class": "form-control", "min": 1}),
        error_messages={
            "required": ProdOperErrors.EMPTY_NUM_WORKERS,
            "min_value": ProdOperErrors.INVALID_NUM_OF_WORKERS,
        },
    )

    class Meta:
        model = ProdOperation
        fields = [
            "prod",
            "tech_oper",
            "profession",
            "center",
            "qualification",
            "num_of_workers",
            "t_pz",
            "t_sht",
        ]
        labels = {
            "prod": "Изделие",
            "tech_oper": "Операция",
            "profession": "Профессия рабочего",
            "center": "Групповой рабочий центр",
            "qualification": "Квалификация рабочего",
            "num_of_workers": "Количество исполнителей",
            "t_pz": "Норма подготовительно-заключительного времени",
            "t_sht": "Норма штучного времени",
        }
        help_texts = {
            "num_of_workers": "Целое положительное число",
            "t_pz": f'Значение по умолчанию: {ProdOperation._meta.get_field("t_pz").default}',
            "t_sht": f'Значение по умолчанию: {ProdOperation._meta.get_field("t_sht").default}',
        }
        widgets = {
            "prod": Select(attrs={"class": "form-control"}),
            "tech_oper": Select(attrs={"class": "form-control"}),
            "profession": Select(attrs={"class": "form-control"}),
            "center": Select(attrs={"class": "form-control"}),
            "qualification": Select(attrs={"class": "form-control"}),
            "t_pz": NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "t_sht": NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }
        error_messages = {
            "prod": {"required": ProdOperErrors.EMPTY_PROD},
            "tech_oper": {"required": ProdOperErrors.EMPTY_TECH_OPER},
            "profession": {"required": ProdOperErrors.EMPTY_PROFESSION},
            "center": {"required": ProdOperErrors.EMPTY_CENTER},
            "qualification": {"required": ProdOperErrors.EMPTY_QUALIFICATION},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["prod"].queryset = Prod.objects.all()
        self.fields["tech_oper"].queryset = ClassStruct.technological_operations()
        self.fields["profession"].queryset = ClassStruct.professions()
        self.fields["qualification"].queryset = ClassStruct.qualifications()


class ProdOperationPosForm(ModelForm):
    input_quantity = DecimalField(
        max_digits=ProdOperationPosConsts.MAX_DIGITS,
        decimal_places=ProdOperationPosConsts.DECIMAL_PLACES,
        min_value=ProdOperationPosConsts.MIN_VALUE,
        required=True,
        label="Расход входного ресурса",
        help_text=f"Минимальное значение: {ProdOperationPosConsts.MIN_VALUE}",
        widget=NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        error_messages={
            "required": ProdOperationPosErrors.EMPTY_INPUT_QUANTITY,
            "min_value": ProdOperationPosErrors.INVALID_INPUT_QUANTITY,
        },
    )
    output_quantity = DecimalField(
        max_digits=ProdOperationPosConsts.MAX_DIGITS,
        decimal_places=ProdOperationPosConsts.DECIMAL_PLACES,
        min_value=ProdOperationPosConsts.MIN_VALUE,
        required=True,
        label="Количество выходного ресурса",
        help_text=f"Минимальное значение: {ProdOperationPosConsts.MIN_VALUE}",
        widget=NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        error_messages={
            "required": ProdOperationPosErrors.EMPTY_OUTPUT_QUANTITY,
            "min_value": ProdOperationPosErrors.INVALID_OUTPUT_QUANTITY,
        },
    )

    class Meta:
        model = ProdOperationPos
        fields = [
            "input_prod_oper",
            "output_prod_oper",
            "input_quantity",
            "output_quantity",
        ]
        labels = {
            "input_prod_oper": "Входная пара <Изделие-операция>",
            "output_prod_oper": "Выходная пара <Изделие-операция>",
        }
        widgets = {
            "input_prod_oper": Select(attrs={"class": "form-control"}),
            "output_prod_oper": Select(attrs={"class": "form-control"}),
        }
        error_messages = {
            "input_prod_oper": {
                "required": ProdOperationPosErrors.EMPTY_INPUT_PROD_OPER
            },
            "output_prod_oper": {
                "required": ProdOperationPosErrors.EMPTY_OUTPUT_PROD_OPER
            },
        }

    def clean_input_quantity(self):
        data = self.cleaned_data.get("input_quantity")
        if data is not None and data < ProdOperationPosConsts.MIN_VALUE:
            raise ValidationError(ProdOperationPosErrors.INVALID_INPUT_QUANTITY)
        return data

    def clean_output_quantity(self):
        data = self.cleaned_data.get("output_quantity")
        if data is not None and data < ProdOperationPosConsts.MIN_VALUE:
            raise ValidationError(ProdOperationPosErrors.INVALID_OUTPUT_QUANTITY)
        return data


ProdOperationPosFormSet = inlineformset_factory(
    parent_model=ProdOperation,
    model=ProdOperationPos,
    form=ProdOperationPosForm,
    fk_name="input_prod_oper",
    fields=(
        "input_quantity",
        "output_quantity",
    ),
    extra=1,
    can_delete=True
)
