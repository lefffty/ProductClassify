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
        self.fields["par_1"] = ModelChoiceField(
            queryset=Agregat.objects.filter(agr=agr),
            label="Параметр 1",
            required=True,
            error_messages={
                "required": AgregatErrors.EMPTY_FIRST_PARAM
            }
        )
        self.fields["par_2"] = ModelChoiceField(
            queryset=Agregat.objects.filter(agr=agr),
            label="Параметр 2",
            required=True,
            error_messages={
                "required": AgregatErrors.EMPTY_SECOND_PARAM
            }
        )

    def clean(self):
        cleaned_data = super().clean()

        par_1: Agregat = cleaned_data.get("par_1")
        par_2: Agregat = cleaned_data.get("par_2")

        if not (par_1 and par_2):
            return cleaned_data

        if par_1 == par_2:
            raise ValidationError(AgregatErrors.SAME_PARAMS)

        with transaction.atomic():
            old_num_1 = par_1.num
            old_num_2 = par_2.num

            temp_num_1 = AgregatConsts.MAX_NUM_VALUE
            temp_num_2 = AgregatConsts.MAX_NUM_VALUE - 1
            par_1.num = temp_num_1
            par_2.num = temp_num_2
            par_1.save(update_fields=["num"])
            par_2.save(update_fields=["num"])

            par_1.num = old_num_2
            par_2.num = old_num_1
            par_1.save(update_fields=["num"])
            par_2.save(update_fields=["num"])

        return cleaned_data
