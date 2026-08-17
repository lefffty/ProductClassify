from django.db import models

from products.models import Prod


class ProdComponent(models.Model):
    parent_prod = models.ForeignKey(
        Prod,
        related_name="parent_prod",
        verbose_name="Родительское изделие",
        on_delete=models.CASCADE,
    )
    component = models.ForeignKey(
        Prod,
        related_name="child_prod",
        verbose_name="Дочернее изделие",
        on_delete=models.CASCADE
    )
    num = models.SmallIntegerField(
        verbose_name="Позиция дочернего изделия к родительскому"
    )
    quantity = models.IntegerField(
        verbose_name="Количество дочернего изделия"
    )

    class Meta:
        verbose_name = "Строка спецификации изделия"
        verbose_name_plural = "Строки спецификации изделия"

    def __str__(self):
        return f"{self.parent_prod.name} - {self.component.name}"
