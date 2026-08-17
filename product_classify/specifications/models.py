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
    quantity = models.FloatField(
        verbose_name="Количество дочернего изделия"
    )

    class Meta:
        verbose_name = "Строка спецификации изделия"
        verbose_name_plural = "Строки спецификации изделия"

    def __str__(self):
        return f"{self.parent_prod.name} - {self.component.name}"


class SpecificationLogs(models.Model):
    pair = models.ForeignKey(
        ProdComponent,
        models.DO_NOTHING,
        blank=False,
        null=False,
        verbose_name="Пара <Родительское изделие - Дочернее изделие>"
    )
    updated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время внесения изменения",
    )
    old_quantity = models.FloatField(
        blank=False,
        null=False,
        verbose_name="Старое количество изделия"
    )
    new_quantity = models.FloatField(
        blank=False,
        null=False,
        verbose_name="Новое количество изделия"
    )

    class Meta:
        verbose_name = "Запись в истории изменений спецификации изделия"
        verbose_name_plural = "Запись в истории изменений спецификации изделия"

    def __str__(self):
        return f"Количество изделия {self.pair.component.name} изменилось с {self.old_quantity} на {self.new_quantity}"
