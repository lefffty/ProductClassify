from django.db import models

from .constants import (
    CLASS_STRUCT_NAME_MAX_LENGTH,
    CLASS_STRUCT_SHORT_NAME_MAX_LENGTH,
)
from ei.models import (
    Ei,
)


class ClassStruct(models.Model):
    name = models.CharField(
        verbose_name='Название класса',
        blank=False,
        null=False,
        max_length=CLASS_STRUCT_NAME_MAX_LENGTH,
    )
    short_name = models.CharField(
        verbose_name='Сокращенное название класса',
        blank=True,
        null=True,
        max_length=CLASS_STRUCT_SHORT_NAME_MAX_LENGTH,
    )
    base_ei = models.ForeignKey(
        Ei,
        verbose_name='Базовая единица измерения',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    main_class = models.ForeignKey(
        'self',
        verbose_name='Родительский класс',
        null=True,
        blank=False,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Классификатор'
        verbose_name_plural = 'Классификатор'

    def __str__(self):
        return self.name


class ParClass(models.Model):
    class_field = models.ForeignKey(
        ClassStruct,
        verbose_name='Класс',
        on_delete=models.DO_NOTHING,
        related_name='class_params'
    )
    parametr = models.ForeignKey(
        'parametr.Parametr',
        verbose_name='Параметр',
        on_delete=models.DO_NOTHING,
    )
    num = models.PositiveSmallIntegerField(
        verbose_name='Позиция в списке параметров класса',
        null=False,
        blank=False,
    )
    min_value = models.FloatField(
        verbose_name='Минимальное значение параметра',
        null=True,
        blank=True,
    )
    max_value = models.FloatField(
        verbose_name='Максимальное значение параметра',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Параметр класса'
        verbose_name_plural = 'Параметры класса'
        constraints = [
            models.UniqueConstraint(
                fields=['class_field', 'parametr'],
                name='%(class)s_pk'
            )
        ]

    def __str__(self):
        return f'{self.class_field.name} - {self.parametr.name}'
