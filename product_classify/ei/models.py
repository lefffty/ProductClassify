from django.db import models

from .constants import EI_NAME_MAX_LENGTH, EI_SHORT_NAME_MAX_LENGTH, EI_CODE_MAX_LENGTH


class Ei(models.Model):
    name = models.CharField(
        verbose_name="Название единицы измерения",
        max_length=EI_NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название единицы измерения",
        max_length=EI_SHORT_NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    code = models.CharField(
        verbose_name="Код единицы измерения",
        max_length=EI_CODE_MAX_LENGTH,
        null=True,
        blank=True,
    )
    convert_factor = models.FloatField(
        verbose_name="Множитель единицы измерения",
        null=True,
        blank=True,
    )
    main_class = models.ForeignKey(
        "self",
        verbose_name="Родительский класс единицы измерения",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"

    def __str__(self):
        if self.short_name is not None:
            return self.short_name
        elif self.name is not None:
            return self.name
        else:
            return "Хуета Лев зачем то говно какое-то добавил"
