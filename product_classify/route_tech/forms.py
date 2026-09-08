from django.forms import (
    Select,
    TextInput,
    ModelForm,
    CharField,
    NumberInput,
    IntegerField,
    ModelChoiceField,
)

from classes.models import ClassStruct
from products.models import Prod

from route_tech.models import (
    GroupWorkingCenter,
    EconomicActivitySubject,
)
from route_tech.models import (
    ProdOperation
)
from route_tech.errors import (
    GWCErrors,
    EASErrors,
    ProdOperErrors,
)
from route_tech.constants import (
    GWCConsts,
    EASConsts,
    ProdOperConsts
)


class EconomicActivitySubjectForm(ModelForm):
    name = CharField(
        label="Название субъекта экономической деятельности",
        max_length=EASConsts.NAME_MAX_LENGTH,
        required=True,
        error_messages={
            "required": EASErrors.EMPTY_NAME,
        }
    )
    short_name = CharField(
        label="Сокращенное название субъекта экономической деятельности",
        max_length=EASConsts.SHORT_NAME_MAX_LENGTH,
        required=True,
        error_messages={
            "required": EASErrors.EMPTY_SHORT_NAME,
        }
    )
    main_class = ModelChoiceField(
        label="Ссылка на класса субъекта экономической деятельности",
        queryset=ClassStruct.objects.none(),
        required=True,
        error_messages={
            "required": EASErrors.EMPTY_MAIN_CLASS,
        }
    )
    main_subject = ModelChoiceField(
        label="Родительский субъект экономичекой деятельности",
        queryset=EconomicActivitySubject.objects.none(),
        required=False
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
    class Meta:
        model = GroupWorkingCenter
        fields = [
            'name',
            'short_name',
            'main_class',
            'eas',
            'place',
        ]
        labels = {
            'name': 'Название группового рабочего центра',
            'short_name': 'Сокращённое название',
            'main_class': 'Родительский класс',
            'eas': 'Субъект экономической деятельности',
            'place': 'Количество рабочих мест',
        }
        help_texts = {
            'name': 'Максимальная длина — {} символов'.format(
                GroupWorkingCenter._meta.get_field('name').max_length
            ),
            'short_name': 'Максимальная длина — {} символов'.format(
                GroupWorkingCenter._meta.get_field('short_name').max_length
            ),
            'place': 'Целое положительное число',
        }
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'short_name': TextInput(attrs={'class': 'form-control'}),
            'main_class': Select(attrs={'class': 'form-control'}),
            'eas': Select(attrs={'class': 'form-control'}),
            'place': NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        error_messages = {
            'name': {
                'required': GWCErrors.EMPTY_NAME,
            },
            'short_name': {
                'required': GWCErrors.EMPTY_SHORT_NAME,
            },
            'main_class': {
                'required': GWCErrors.EMPTY_MAIN_CLASS,
            },
            'eas': {
                'required': GWCErrors.EMPTY_EAS,
            },
            'place': {
                'required': GWCErrors.EMPTY_PLACE,
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['main_class'].queryset = ClassStruct.means_of_labor()
        self.fields['eas'].queryset = EconomicActivitySubject.objects.all()


class ProdOperationForm(ModelForm):
    num_of_workers = IntegerField(
        required=True,
        min_value=1,
        widget=NumberInput(attrs={'class': 'form-control', 'min': 1}),
        error_messages={'required': ProdOperErrors.EMPTY_NUM_WORKERS}
    )

    class Meta:
        model = ProdOperation
        fields = [
            'prod',
            'tech_oper',
            'profession',
            'center',
            'qualification',
            'num_of_workers',
            't_pz',
            't_sht',
        ]
        labels = {
            'prod': 'Изделие',
            'tech_oper': 'Операция',
            'profession': 'Профессия рабочего',
            'center': 'Групповой рабочий центр',
            'qualification': 'Квалификация рабочего',
            'num_of_workers': 'Количество исполнителей',
            't_pz': 'Норма подготовительно-заключительного времени',
            't_sht': 'Норма штучного времени',
        }
        help_texts = {
            'num_of_workers': 'Целое положительное число',
            't_pz': f'Значение по умолчанию: {ProdOperation._meta.get_field("t_pz").default}',
            't_sht': f'Значение по умолчанию: {ProdOperation._meta.get_field("t_sht").default}',
        }
        widgets = {
            'prod': Select(attrs={'class': 'form-control'}),
            'tech_oper': Select(attrs={'class': 'form-control'}),
            'profession': Select(attrs={'class': 'form-control'}),
            'center': Select(attrs={'class': 'form-control'}),
            'qualification': Select(attrs={'class': 'form-control'}),
            't_pz': NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            't_sht': NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        error_messages = {
            'prod': {'required': ProdOperErrors.EMPTY_PROD},
            'tech_oper': {'required': ProdOperErrors.EMPTY_TECH_OPER},
            'profession': {'required': ProdOperErrors.EMPTY_PROFESSION},
            'center': {'required': ProdOperErrors.EMPTY_CENTER},
            'qualification': {'required': ProdOperErrors.EMPTY_QUALIFICATION},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prod'].queryset = Prod.objects.all()
        self.fields['tech_oper'].queryset = ClassStruct.technological_operations()
        self.fields['profession'].queryset = ClassStruct.professions()
        self.fields['qualification'].queryset = ClassStruct.qualifications()
