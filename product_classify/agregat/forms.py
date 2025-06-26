from django.forms import (
    ModelForm,
    ModelChoiceField,
    Form,
)

from .models import Agregat
from parametr.models import Parametr


class AgregatForm(ModelForm):
    agr = ModelChoiceField(
        queryset=Parametr.agregats.all(),
        label='Агрегат',
    )
    par = ModelChoiceField(
        queryset=Parametr.parameters.all(),
        label='Параметр',
    )

    class Meta:
        model = Agregat
        fields = ['agr', 'par']

    def __init__(self, *args, **kwargs):
        agr = kwargs.pop('agr', None)
        super().__init__(*args, **kwargs)
        self.fields['agr'].queryset = Parametr.agregats.all()
        self.fields['par'].queryset = Parametr.parameters.all()
        self.fields['agr'].initial = agr


class ChangeAgregatNumForm(Form):
    def __init__(self, *args, **kwargs):
        agr = kwargs.pop('agr', None)
        super().__init__(*args, **kwargs)
        self.fields['agr_param_1'] = ModelChoiceField(
            queryset=Agregat.objects.filter(agr=agr),
            label='Параметр 1',
        )
        self.fields['agr_param_2'] = ModelChoiceField(
            queryset=Agregat.objects.filter(agr=agr),
            label='Параметр 2',
        )
