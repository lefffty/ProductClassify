from django.db.models import Model
from django.forms import (
    ModelForm,
    ModelChoiceField,
    Form,
)

from parametr.models import Parametr

from .models import Agregat


class AgregatForm(ModelForm):
    agr = ModelChoiceField(
        label="Агрегат",
        queryset=Parametr.objects.none(),
    )
    par = ModelChoiceField(
        label="Параметр",
        queryset=Parametr.objects.none(),
    )

    class Meta:
        model = Agregat
        fields = ("agr", "par")

    def __init__(self, *args, **kwargs):
        agr = kwargs.pop("agr", None)
        super().__init__(*args, **kwargs)
        self.fields["agr"].queryset = Parametr.agregats()
        self.fields["par"].queryset = Parametr.parameters()
        self.fields["agr"].initial = agr


class ChangeAgregatNumForm(Form):
    def __init__(self, *args, **kwargs):
        agr = kwargs.pop("agr", None)
        super().__init__(*args, **kwargs)
        self.fields["agr_param_1"] = ModelChoiceField(
            queryset=Agregat.objects.filter(agr=agr),
            label="Параметр 1",
        )
        self.fields["agr_param_2"] = ModelChoiceField(
            queryset=Agregat.objects.filter(agr=agr),
            label="Параметр 2",
        )

    def clean(self):
        print(self.fields)
        cleaned_data = super().clean()
        agr_param_1 = cleaned_data["agr_param_1"]
        agr_param_2 = cleaned_data["agr_param_2"]
        temp_num = agr_param_1.num
        agr_param_1.num = agr_param_2.num
        agr_param_2.num = temp_num
        agr_param_1.save()
        agr_param_2.save()
        return cleaned_data
