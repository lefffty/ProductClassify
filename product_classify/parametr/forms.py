from django.forms import ModelForm, ModelChoiceField, CharField
from django.core.exceptions import ValidationError

from classes.models import ClassStruct
from classes.constants import EnumsIds, ParamIds
from ei.models import Ei

from parametr.models import Parametr
from parametr.constants import ParametrConsts
from parametr.errors import ParametrErrors


class ParametrForm(ModelForm):
    parametr_type = ModelChoiceField(
        label="Тип параметра",
        queryset=ClassStruct.objects.none(),
        required=True,
    )
    par_ei = ModelChoiceField(
        label="Единица измерения параметра",
        queryset=Ei.objects.none(),
        required=False,
    )
    name = CharField(
        max_length=ParametrConsts.NAME_MAX_LENGTH,
        required=True,
        label="Название параметра",
    )
    short_name = CharField(
        max_length=ParametrConsts.SHORT_NAME_MAX_LENGTH,
        required=False,
        label="Сокращенное название параметра",
    )

    class Meta:
        model = Parametr
        fields = (
            "parametr_type",
            "name",
            "short_name",
            "par_ei",
        )
        labels = {
            "parametr_type": "Тип параметра",
            "name": "Название параметра",
            "short_name": "Сокращенное название параметра",
            "par_ei": "Единица измерения параметра",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parametr_type"].queryset = ClassStruct.parametr_types()
        self.fields["par_ei"].queryset = Ei.objects.all()

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get("name")

        if not name:
            raise ValidationError(ParametrErrors.EMPTY_NAME)

        short_name = cleaned_data.get("short_name")

        if not short_name:
            raise ValidationError(ParametrErrors.EMPTY_SHORT_NAME)

        parametr_tp = cleaned_data.get("parametr_type")

        if not parametr_tp:
            raise ValidationError(ParametrErrors.EMPTY_PAR_TYPE)

        par_ei = cleaned_data.get("par_ei")

        str_enum = ClassStruct.objects.get(pk=EnumsIds.STRING)
        img_enum = ClassStruct.objects.get(pk=EnumsIds.IMAGE)
        agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)

        if parametr_tp == str_enum and par_ei is not None:
            raise ValidationError(ParametrErrors.STRING_ENUM)
        
        elif parametr_tp == img_enum and par_ei is not None:
            raise ValidationError(ParametrErrors.IMAGE_ENUM)
        
        elif parametr_tp == agregat_type and par_ei is not None:
            raise ValidationError(ParametrErrors.AGREGAT)
        
        return cleaned_data
