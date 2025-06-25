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
        blank=False,
        null=False,
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
