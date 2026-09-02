from django.db.models import (
    Model,
    CharField,
    CASCADE,
    ForeignKey
)

from classes.models import ClassStruct

from route_tech.constants import EASConsts


class EconomicActivitySubject(Model):
    name = CharField(
        verbose_name="Название субъекта экономической деятельности",
        max_length=EASConsts.NAME_MAX_LENGTH,
        blank=False,
        null=False,
    )
    short_name = CharField(
        verbose_name="Сокращенное название субъекта экономической деятельности",
        max_length=EASConsts.SHORT_NAME_MAX_LENGTH,
        blank=False,
        null=False,
    )
    main_class = ForeignKey(
        ClassStruct,
        on_delete=CASCADE,
        verbose_name="Ссылка на класс субъекта экономической деятельности",
        related_name="subjects_by_class",
        null=False,
    )
    main_subject = ForeignKey(
        "self",
        verbose_name="Родительский субъект экономической деятельности",
        related_name="children",
        on_delete=CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = "Субъект экономической деятельности"
        verbose_name_plural = "Субъекты экономической деятельности"

    def __str__(self):
        return self.name
