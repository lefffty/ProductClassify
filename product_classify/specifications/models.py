from django.db import models, connection

from core.queries import DatabaseFunctions

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

    @classmethod
    def is_parent_prod(cls, product_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                DatabaseFunctions.IS_PARENT_PROD,
                params=[product_id]
            )
            is_parent = cursor.fetchone()[0]
        return is_parent

    @classmethod
    def total_cost_ratio(cls, product_id: int, number_of_products: int):
        with connection.cursor() as cursor:
            cursor.execute(
                DatabaseFunctions.TOTAL_COST_RATIO,
                params=[product_id, number_of_products]
            )
            results = cursor.fetchall()
        return results

    @classmethod
    def product_specification(cls, product_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                DatabaseFunctions.PRODUCT_SPECIFICATION,
                params=[product_id]
            )
            results = cursor.fetchall()
        return results


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

    @classmethod
    def get_changelog(cls, product_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                DatabaseFunctions.GET_CHANGE_LOG,
                params=[product_id]
            )
            results = cursor.fetchall()
        return results
