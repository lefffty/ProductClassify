from django.core.exceptions import ValidationError
from django.db import models

from classes.models import ClassStruct, ParClass
from parametr.models import Parametr
from enums.models import Enums
from products.constants import INT_PARAMS, DOUBLE_PARAMS

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
        blank=True,
        verbose_name="Целочисленное значение параметра",
    )
    double_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Вещественное значение параметра",
    )
    enum_val = models.ForeignKey(
        Enums,
        verbose_name="Значение перечисления параметра",
        null=True,
        blank=True,
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

    def clean(self):
        cls_id = self.prod.class_field.id
        class_params_ids = ParClass.objects.filter(class_field=cls_id).values_list(
            "parametr", flat=True
        )

        if self.par.id not in class_params_ids:
            raise ValidationError(
                "Параметр '{}' не принадлежит классу изделия '{}'.".format(
                    self.par.name, self.prod.class_field.name
                )
            )

        # параметр является перечислением строк
        if self.par.parametr_type.pk == ENUM_CLASSES_IDS[0] and (
            self.enum_val.enum.main_class.pk != ENUM_CLASSES_IDS[0] or not self.enum_val
        ):
            raise ValidationError(
                "Для параметра типа 'Строковое перечисление' необходимо выбрать значение из списка строковых перечислений."
            )
        # параметр является перечислением изображений
        elif self.par.parametr_type.pk == ENUM_CLASSES_IDS[1] and (
            self.enum_val.enum.main_class.pk != ENUM_CLASSES_IDS[1] or not self.enum_val
        ):
            raise ValidationError(
                "Для параметра типа 'Перечисление изображений' необходимо выбрать значение из списка перечислений изображений."
            )
        # параметр является целочисленным перечислением
        elif self.par.parametr_type.pk == ENUM_CLASSES_IDS[2] and (
            self.enum_val.enum.main_class.pk != ENUM_CLASSES_IDS[2] or not self.enum_val
        ):
            raise ValidationError(
                "Для параметра типа 'Целочисленное перечисление' необходимо выбрать значение из списка целочисленных перечислений."
            )
        # параметр является вещественным перечислением
        elif self.par.parametr_type.pk == ENUM_CLASSES_IDS[3] and (
            self.enum_val.enum.main_class.pk != ENUM_CLASSES_IDS[3] or not self.enum_val
        ):
            raise ValidationError(
                "Для параметра типа 'Вещественное перечисление' необходимо выбрать значение из списка вещественных перечислений."
            )
        # параметр является целочисленным
        elif self.par.parametr_type.pk == INT_PARAMS and not self.int_value:
            raise ValidationError(
                "Для параметра типа 'Целое число' необходимо указать целочисленное значение."
            )
        # параметр является вещественным
        elif self.par.parametr_type.pk == DOUBLE_PARAMS and not self.double_value:
            raise ValidationError(
                "Для параметра типа 'Вещественное число' необходимо указать вещественное значение."
            )

    def __str__(self):
        # параметр является перечислением
        if self.enum_val:
            # перечисление строк
            if self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[0]:
                return self.prod.name + " - " + self.enum_val.name
            # перечисление изображений
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[1]:
                return self.prod.name + " - " + self.enum_val.short_name
            # вещественное перечисление
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[2]:
                return (
                    self.prod.name
                    + " - "
                    + self.enum_val.short_name
                    + " - "
                    + str(self.enum_val.double_value)
                )
            # целочисленное перечисление
            else:
                return (
                    self.prod.name
                    + " - "
                    + self.enum_val.short_name
                    + " - "
                    + str(self.enum_val.int_value)
                )
        # параметр является целочисленным
        elif self.int_value:
            return self.prod.name + " - " + self.par.name + " - " + str(self.int_value)
        # параметр является вещественным
        else:
            return (
                self.prod.name + " - " + self.par.name + " - " + str(self.double_value)
            )

    def get_value(self):
        # параметр является целочисленным
        if self.int_value:
            return self.int_value
        # параметр является вещественным
        elif self.double_value:
            return self.double_value
        # параметр является перечислением
        else:
            # перечисление строк
            if self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[0]:
                return self.enum_val.name
            # перечисление изображений
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[1]:
                return self.enum_val.image.instance
            # вещественное перечисление
            elif self.enum_val.enum.main_class.id == ENUM_CLASSES_IDS[2]:
                return self.enum_val.double_value
            # целочисленное перечисление
            else:
                return self.enum_val.int_value
