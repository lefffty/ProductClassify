from django.db import models

from products.models import Prod
from specifications.constants import ProdComponentConsts


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
        on_delete=models.CASCADE,
    )
    num = models.SmallIntegerField(
        verbose_name="Позиция дочернего изделия к родительскому"
    )
    quantity = models.DecimalField(
        verbose_name="Количество дочернего изделия",
        max_digits=ProdComponentConsts.MAX_DIGITS,
        decimal_places=ProdComponentConsts.DECIMAL_PLACES,
    )

    class Meta:
        verbose_name = "Строка спецификации изделия"
        verbose_name_plural = "Строки спецификации изделия"
        permissions = [
            (
                "can_get_total_cost_ratio",
                "Может производить расчет норм расхода материальных ресурсов",
            ),
            (
                "can_get_product_changelog",
                "Может получить историю изменений спецификации изделия",
            ),
            (
                "can_edit_specification",
                "Может редактировать спецификацию изделия"
            ),
        ]

    def __str__(self):
        return f"{self.parent_prod.name} - {self.component.name}"


class SpecificationLogs(models.Model):
    pair = models.ForeignKey(
        ProdComponent,
        models.SET_NULL,
        blank=False,
        null=True,
        verbose_name="Пара <Родительское изделие - Дочернее изделие>",
    )
    updated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время внесения изменения",
    )
    old_quantity = models.DecimalField(
        blank=False,
        null=False,
        verbose_name="Старое количество изделия",
        max_digits=ProdComponentConsts.MAX_DIGITS,
        decimal_places=ProdComponentConsts.DECIMAL_PLACES,
    )
    new_quantity = models.DecimalField(
        blank=False,
        null=False,
        verbose_name="Новое количество изделия",
        max_digits=ProdComponentConsts.MAX_DIGITS,
        decimal_places=ProdComponentConsts.DECIMAL_PLACES,
    )

    class Meta:
        verbose_name = "Запись в истории изменений спецификации изделия"
        verbose_name_plural = "Запись в истории изменений спецификации изделия"

    def __str__(self):
        return f"Количество изделия {self.pair.component.name} изменилось с {self.old_quantity} на {self.new_quantity}"
