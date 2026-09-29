from django.db import models, transaction

from parametr.models import (
    Parametr,
)


class Agregat(models.Model):
    agr = models.ForeignKey(
        Parametr,
        verbose_name="Агрегат",
        on_delete=models.CASCADE,
        related_name="agregat_parametrs",
    )
    par = models.ForeignKey(
        Parametr,
        verbose_name="Параметр",
        on_delete=models.CASCADE,
    )
    num = models.PositiveSmallIntegerField(
        verbose_name="Номер позиции в агрегате",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Агрегат"
        verbose_name_plural = "Агрегаты"
        constraints = [
            models.UniqueConstraint(
                fields=["agr", "par"],
                name="%(class)s_pk",
            )
        ]

    def delete(self, *args, **kwargs):
        agr_id = self.agr_id
        num = self.num

        with transaction.atomic():
            result = super().delete(*args, **kwargs)
            Agregat.objects.filter(
                agr_id=agr_id,
                num__gt=num,
            ).update(num=models.F("num") - 1)

        return result

    def __str__(self):
        return f"{self.agr.name} - {self.par.name}"
