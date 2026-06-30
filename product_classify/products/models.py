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
        cls_id = self.prod.class_field.pk
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
            not self.enum_val or self.enum_val.enum.main_class.pk != ENUM_CLASSES_IDS[0]
        ):
            raise ValidationError(
                "Для параметра типа 'Строковое перечисление' необходимо выбрать значение из списка строковых перечислений."
            )
        # параметр является перечислением изображений
        elif self.par.parametr_type.pk == ENUM_CLASSES_IDS[1] and (
            not self.enum_val or self.enum_val.enum.main_class.pk != ENUM_CLASSES_IDS[1]
        ):
            raise ValidationError(
                "Для параметра типа 'Перечисление изображений' необходимо выбрать значение из списка перечислений изображений."
            )
        # параметр является целочисленным перечислением
        elif self.par.parametr_type.pk == ENUM_CLASSES_IDS[2] and (
            not self.enum_val or self.enum_val.enum.main_class.pk != ENUM_CLASSES_IDS[2]
        ):
            raise ValidationError(
                "Для параметра типа 'Вещественное перечисление' необходимо выбрать значение из списка вещественных перечислений."
            )
        # параметр является вещественным перечислением
        elif self.par.parametr_type.pk == ENUM_CLASSES_IDS[3] and (
            not self.enum_val or self.enum_val.enum.main_class.pk != ENUM_CLASSES_IDS[3]
        ):
            raise ValidationError(
                "Для параметра типа 'Целочисленное перечисление' необходимо выбрать значение из списка целочисленных перечислений."
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

    def _get_enum_display_value(self):
        """Возвращает строковое представление для значения перечисления в зависимости от его типа."""
        enum_type_id = self.enum_val.enum.main_class.id
        if enum_type_id == ENUM_CLASSES_IDS[0]:  # строковое
            return self.enum_val.name
        elif enum_type_id == ENUM_CLASSES_IDS[1]:  # изображение
            return self.enum_val.short_name
        elif enum_type_id == ENUM_CLASSES_IDS[2]:  # вещественное
            return f"{self.enum_val.short_name} - {self.enum_val.double_value}"
        else:  # целочисленное
            return f"{self.enum_val.short_name} - {self.enum_val.int_value}"

    def _get_enum_raw_value(self):
        """Возвращает сырое значение перечисления (для get_value)."""
        enum_type_id = self.enum_val.enum.main_class.id
        if enum_type_id == ENUM_CLASSES_IDS[0]:
            return self.enum_val.name
        elif enum_type_id == ENUM_CLASSES_IDS[1]:
            return self.enum_val.image
        elif enum_type_id == ENUM_CLASSES_IDS[2]:
            return self.enum_val.double_value
        else:
            return self.enum_val.int_value

    def __str__(self):
        if self.enum_val:
            return f"{self.prod.name} - {self._get_enum_display_value()}"
        elif self.int_value is not None:  # явная проверка на None
            return f"{self.prod.name} - {self.par.name} - {self.int_value}"
        else:
            return f"{self.prod.name} - {self.par.name} - {self.double_value}"

    def get_value(self):
        if self.int_value is not None:
            return self.int_value
        elif self.double_value is not None:
            return self.double_value
        elif self.enum_val:
            return self._get_enum_raw_value()
        else:
            return None  # или выбросить исключение, если недопустимо
