from django.db import models

from classes.models import (
    ClassStruct,
)
from .constants import (
    ENUMS_NAME_MAX_LENGTH,
    ENUMS_SHORT_NAME_MAX_LENGTH,
)


class Enums(models.Model):
    enum = models.ForeignKey(
        ClassStruct,
        verbose_name='Родительский класс',
        on_delete=models.CASCADE,
    )
    num = models.PositiveSmallIntegerField(
        verbose_name='Номер позиции в перечислении',
        null=False,
        blank=False,
    )
    name = models.CharField(
        verbose_name='Название перечисления',
        max_length=ENUMS_NAME_MAX_LENGTH,
        null=True,
    )
    short_name = models.CharField(
        verbose_name='Сокращенное название перечисления',
        max_length=ENUMS_SHORT_NAME_MAX_LENGTH,
        null=True,
    )
    double_value = models.FloatField(
        verbose_name='Вещественное значение перечисления',
        null=True,
        blank=True,
    )
    int_value = models.IntegerField(
        verbose_name='Целочисленное значение перечисления',
        null=True,
        blank=True,
    )
    image = models.ImageField(
        verbose_name='Изображение перечисления',
        upload_to='enum_images/',
    )

    class Meta:
        verbose_name = 'Значение перечисления'
        verbose_name_plural = 'Значения перечисления'

    def __str__(self):
        return self.short_name
