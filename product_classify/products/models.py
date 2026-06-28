from django.db import models

from classes.models import ClassStruct
from parametr.models import (
    Parametr,
)
from enums.models import (
    Enums,
)

from .constants import (
    ENUM_CLASSES_IDS,
    PROD_NAME_MAX_LENGTH,
    PROD_SHORT_NAME_MAX_LENGTH,
)


class Prod(models.Model):
    name = models.CharField(
        verbose_name="Название изделия",
        null=False,
        blank=False,
        max_length=PROD_NAME_MAX_LENGTH,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название изделия",
        null=False,
        blank=True,
        max_length=PROD_SHORT_NAME_MAX_LENGTH,
    )
    class_field = models.ForeignKey(
        ClassStruct,
        verbose_name="Родительский класс",
        null=False,
        on_delete=models.CASCADE,
        related_name="class_products",
    )
    image = models.ImageField(
        verbose_name="Изображение изделия",
        blank=False,
        null=False,
        upload_to="product_images/",
    )

    class Meta:
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"

    def __str__(self):
        return self.name


class ParProd(models.Model):
    prod = models.ForeignKey(
        Prod,
        verbose_name="Изделие",
        on_delete=models.CASCADE,
        related_name="product_params",
    )
    par = models.ForeignKey(
        Parametr,
        verbose_name="Параметр",
        on_delete=models.CASCADE,
    )
    int_value = models.PositiveSmallIntegerField(
        null=True,
        blank=False,
        verbose_name="Целочисленное значение параметра",
    )
    double_value = models.FloatField(
        null=True,
        blank=False,
        verbose_name="Вещественное значение параметра",
    )
    enum_val = models.ForeignKey(
        Enums,
        verbose_name="Значение перечисления параметра",
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Параметр изделия"
        verbose_name_plural = "Параметры изделий"
        constraints = [
            models.UniqueConstraint(
                fields=["prod", "par"],
                name="%(class)s_pk",
            )
        ]

    def __str__(self):
        if self.enum_val:
            if self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[0]:
                return self.prod.name + " - " + self.enum_val.name
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[1]:
                return self.prod.name + " - " + self.enum_val.short_name
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[2]:
                return (
                    self.prod.name
                    + " - "
                    + self.enum_val.short_name
                    + " - "
                    + str(self.enum_val.double_value)
                )
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[3]:
                return (
                    self.prod.name
                    + " - "
                    + self.enum_val.short_name
                    + " - "
                    + str(self.enum_val.int_value)
                )
        if self.int_value:
            return self.prod.name + " - " + self.par.name + " - " + str(self.int_value)
        if self.double_value:
            return (
                self.prod.name + " - " + self.par.name + " - " + str(self.double_value)
            )

    def get_value(self):
        if self.int_value:
            return self.int_value
        elif self.double_value:
            return self.double_value
        elif self.enum_val:
            if self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[0]:
                return self.enum_val.name
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[1]:
                return self.enum_val.image.instance
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[2]:
                return self.enum_val.double_value
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[3]:
                return self.enum_val.int_value
