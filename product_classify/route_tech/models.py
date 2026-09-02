from django.db.models import (
    Model,
    CharField,
    CASCADE,
    ForeignKey,
    PositiveSmallIntegerField
)

from classes.models import ClassStruct

from route_tech.constants import EASConsts, GWCConsts


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


class GroupWorkingCenter(Model):
    name = CharField(
        verbose_name="Название группового рабочего центра",
        max_length=GWCConsts.NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    short_name = CharField(
        verbose_name="Сокращенное название группового рабочего центра",
        max_length=GWCConsts.SHORT_NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    main_class = ForeignKey(
        ClassStruct,
        on_delete=CASCADE,
        verbose_name="Ссылка на родительский класс",
        related_name="working_centers_by_class",
        null=False,
    )
    eas = ForeignKey(
        EconomicActivitySubject,
        on_delete=CASCADE,
        verbose_name="Ссылка на субъект экономической деятельности",
        related_name="working_centers_by_subject",
        null=False,
    )
    place = PositiveSmallIntegerField(
        verbose_name="Количество рабочих мест на групповом рабочим центре",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Групповой рабочий центр"
        verbose_name_plural = "Групповые рабочие центры"

    def __str__(self):
        return self.name
