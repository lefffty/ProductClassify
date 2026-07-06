from django.core.exceptions import ValidationError
from django.forms import (
    ModelForm,
    ModelChoiceField,
    Form,
)
from loguru import logger

from parametr.models import Parametr

from .models import Agregat


class AgregatForm(ModelForm):
    agr = ModelChoiceField(
        label="Агрегат",
        queryset=Parametr.objects.none(),
        required=True,
    )
    par = ModelChoiceField(
        label="Параметр",
        queryset=Parametr.objects.none(),
        required=True,
    )

    class Meta:
        model = Agregat
        fields = (
            "agr",
            "par",
        )

    def __init__(self, *args, **kwargs):
        agr = kwargs.pop("agr", None)
        super().__init__(*args, **kwargs)
        self.fields["agr"].queryset = Parametr.agregats()
        self.fields["par"].queryset = Parametr.parameters()
        self.fields["agr"].initial = agr

    def clean(self):
        cleaned_data = super().clean()
        agr = cleaned_data.get("agr")

        if agr and not self.instance.pk:
            cleaned_data["num"] = Agregat.objects.filter(agr=agr).count() + 1

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if "num" in self.cleaned_data:
            instance.num = self.cleaned_data["num"]
        if commit:
            instance.save()
        return instance


class ChangeAgregatNumForm(Form):
    def __init__(self, *args, **kwargs):
        agr = kwargs.pop("agr", None)
        super().__init__(*args, **kwargs)
        self.fields["agr_param_1"] = ModelChoiceField(
            queryset=Agregat.objects.filter(agr=agr),
            label="Параметр 1",
            required=True,
        )
        self.fields["agr_param_2"] = ModelChoiceField(
            queryset=Agregat.objects.filter(agr=agr),
            label="Параметр 2",
            required=True,
        )

    def clean(self):
        cleaned_data = super().clean()
        agr_param_1 = cleaned_data.get("agr_param_1")

        if not agr_param_1:
            raise ValidationError(
                "Поле первого параметра агрегата в форме необходимо заполнить"
            )

        agr_param_2 = cleaned_data.get("agr_param_2")

        if not agr_param_2:
            raise ValidationError(
                "Поле второго параметра агрегата в форме необходимо заполнить"
            )

        if agr_param_1 == agr_param_2:
            raise ValidationError("Выберите разные параметры")

        temp_num = agr_param_1.num
        agr_param_1.num = agr_param_2.num
        agr_param_2.num = temp_num
        agr_param_1.save()
        agr_param_2.save()
        return cleaned_data
