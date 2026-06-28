from django.db import models

from classes.models import ClassStruct
from ei.models import Ei

from .constants import (
    PARAMETR_NAME_MAX_LENGTH,
    PARAMETR_SHORT_NAME_MAX_LENGTH,
    AGREGAT_TYPE_ID,
)


class Parametr(models.Model):
    name = models.CharField(
        verbose_name="Название параметра",
        max_length=PARAMETR_NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название параметра",
        max_length=PARAMETR_SHORT_NAME_MAX_LENGTH,
        null=False,
        blank=True,
    )
    parametr_type = models.ForeignKey(
        ClassStruct,
        verbose_name="Тип параметра",
        on_delete=models.CASCADE,
        null=False,
        related_name="type_parameters",
    )
    par_ei = models.ForeignKey(
        Ei,
        verbose_name="Единица измерения параметра",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Параметры"

    def __str__(self):
        if self.par_ei is not None:
            return self.name + ", " + self.par_ei.short_name
        else:
            return self.name

    @classmethod
    def parameters(cls):
        return cls.objects.exclude(parametr_type__exact=AGREGAT_TYPE_ID)

    @classmethod
    def agregats(cls):
        return cls.objects.filter(parametr_type__exact=AGREGAT_TYPE_ID)
