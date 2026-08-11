from django.db import models

from ei.constants import EiConsts


class Ei(models.Model):
    name = models.CharField(
        verbose_name="Название единицы измерения",
        max_length=EiConsts.NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название единицы измерения",
        max_length=EiConsts.SHORT_NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    code = models.CharField(
        verbose_name="Код единицы измерения",
        max_length=EiConsts.CODE_MAX_LENGTH,
        null=False,
        blank=True,
    )
    convert_factor = models.FloatField(
        verbose_name="Множитель единицы измерения",
        null=True,
        blank=False,
    )
    main_class = models.ForeignKey(
        "self",
        verbose_name="Родительский класс единицы измерения",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="child_eis",
    )

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"

    def __str__(self):
        return self.short_name
