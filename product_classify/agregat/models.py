from django.db import models

from parametr.models import (
    Parametr,
)


class Agregat(models.Model):
    agr = models.ForeignKey(
        Parametr,
        verbose_name='Агрегат',
        on_delete=models.DO_NOTHING,
        related_name='agregat_parametrs',
    )
    par = models.ForeignKey(
        Parametr,
        verbose_name='Параметр',
        on_delete=models.DO_NOTHING,
    )
    num = models.PositiveSmallIntegerField(
        verbose_name='Номер позиции в агрегате',
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = 'Агрегат'
        verbose_name_plural = 'Агрегаты'
        constraints = [
            models.UniqueConstraint(
                fields=['agr', 'par'],
                name='%(class)s_pk',
            )
        ]

    def __str__(self):
        return f'{self.agr.name} - {self.par.name}'
