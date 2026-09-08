from django.forms import (
    ModelForm,
    CharField,
    ModelChoiceField,
)

from classes.models import ClassStruct

from route_tech.models import (
    EconomicActivitySubject
)
from route_tech.errors import (
    EASErrors
)
from route_tech.constants import (
    EASConsts
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
