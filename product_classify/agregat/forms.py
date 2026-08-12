from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import (
    ModelForm,
    ModelChoiceField,
    Form,
)

from parametr.models import Parametr

from agregat.models import Agregat
from agregat.constants import AgregatConsts
from agregat.errors import AgregatErrors


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
        agr_param_1: Agregat = cleaned_data.get("agr_param_1")

        if not agr_param_1:
            raise ValidationError(AgregatErrors.EMPTY_FIRST_PARAM)

        agr_param_2: Agregat = cleaned_data.get("agr_param_2")

        if not agr_param_2:
            raise ValidationError(AgregatErrors.EMPTY_SECOND_PARAM)

        if agr_param_1 == agr_param_2:
            raise ValidationError(AgregatErrors.SAME_PARAMS)

        with transaction.atomic():
            old_num_1 = agr_param_1.num
            old_num_2 = agr_param_2.num

            temp_num_1 = AgregatConsts.MAX_NUM_VALUE
            temp_num_2 = AgregatConsts.MAX_NUM_VALUE - 1
            agr_param_1.num = temp_num_1
            agr_param_2.num = temp_num_2
            agr_param_1.save(update_fields=["num"])
            agr_param_2.save(update_fields=["num"])

            agr_param_1.num = old_num_2
            agr_param_2.num = old_num_1
            agr_param_1.save(update_fields=["num"])
            agr_param_2.save(update_fields=["num"])

        return cleaned_data
