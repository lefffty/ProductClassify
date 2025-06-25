from django.db import models

from classes.models import (
    ClassStruct
)
from parametr.models import (
    Parametr,
)
from enums.models import (
    Enums,
)
from .constants import (
    PROD_NAME_MAX_LENGTH,
    PROD_SHORT_NAME_MAX_LENGTH,
)


class Prod(models.Model):
    name = models.CharField(
        verbose_name='Название изделия',
        null=False,
        blank=False,
        max_length=PROD_NAME_MAX_LENGTH,
    )
    short_name = models.CharField(
        verbose_name='Сокращенное название изделия',
        null=True,
        blank=False,
        max_length=PROD_SHORT_NAME_MAX_LENGTH,
    )
    class_field = models.ForeignKey(
        ClassStruct,
        verbose_name='Родительский класс',
        null=False,
        blank=False,
        on_delete=models.DO_NOTHING,
        related_name='class_products',
    )
    image = models.ImageField(
        verbose_name='Изображение изделия',
        blank=False,
        null=False,
        upload_to='product_images/',
    )

    class Meta:
        verbose_name = 'Изделие'
        verbose_name_plural = 'Изделия'

    def __str__(self):
        return self.short_name


class ParProd(models.Model):
    prod = models.ForeignKey(
        Prod,
        verbose_name='Изделие',
        on_delete=models.CASCADE,
        related_name='product_params',
    )
    par = models.ForeignKey(
        Parametr,
        verbose_name='Параметр',
        on_delete=models.CASCADE,
    )
    int_value = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Целочисленное значение параметра',
    )
    double_value = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Вещественное значение параметра',
    )
    enum_val = models.ForeignKey(
        Enums,
        verbose_name='Значение перечисления параметра',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Параметр изделия'
        verbose_name_plural = 'Параметры изделий'
        constraints = [
            models.UniqueConstraint(
                fields=['prod', 'par'],
                name='%(class)s_pk',
            )
        ]
