from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, connection

from collections import namedtuple

from classes.models import ClassStruct, ParClass
from classes.constants import ParamIds,EnumsIds
from parametr.models import Parametr
from core.queries import ProdQueries
from enums.models import Enums
from ei.models import Ei
from products.constants import ProdConsts


ModificationResult = namedtuple(
    "ModificationResult",
    field_names=[
        "modification_id"
    ]
)


class Prod(models.Model):
    name = models.CharField(
        verbose_name="Название изделия",
        null=False,
        blank=False,
        max_length=ProdConsts.NAME_MAX_LENGTH,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название изделия",
        null=False,
        blank=True,
        max_length=ProdConsts.SHORT_NAME_MAX_LENGTH,
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
    cost = models.DecimalField(
        blank=True,
        null=True,
        verbose_name="Стоимость изделия",
        max_digits=ProdConsts.MAX_DIGITS,
        decimal_places=ProdConsts.DECIMAL_PLACES,
        validators=[
            MinValueValidator(ProdConsts.MIN_COST)
        ],
    )
    modification = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Базовое изделие",
    )
    ei = models.ForeignKey(
        Ei,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name="Единица измерения изделия",
    )

    class Meta:
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"

    def __str__(self):
        return self.name

    @classmethod
    def create_modification(self, product_id: int, name: str, short_name: str) -> ModificationResult:
        with connection.cursor() as cursor:
            params = [product_id, name, short_name]
            cursor.execute(
                ProdQueries.CREATE_MODIFICATION,
                params=params
            )
            row = cursor.fetchall()[0]
        return ModificationResult(*row)


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
        if not self.prod_id:
            return

        if not self.par_id:
            return

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
        if self.par.parametr_type.pk == EnumsIds.STRING and (
            not self.enum_val or
            any([self.double_value, self.int_value]) or # если для параметра-перечисления строк указаны значения полей int_value, double_value
            self.enum_val.enum.main_class.pk != EnumsIds.STRING
        ):
            raise ValidationError(
                "Для параметра типа 'Строковое перечисление' необходимо выбрать значение из списка строковых перечислений."
            )
        # параметр является перечислением изображений
        elif self.par.parametr_type.pk == EnumsIds.IMAGE and (
            not self.enum_val or
            any([self.double_value, self.int_value]) or # если для параметра-перечисления изображений указаны значения полей int_value, double_value
            self.enum_val.enum.main_class.pk != EnumsIds.IMAGE
        ):
            raise ValidationError(
                "Для параметра типа 'Перечисление изображений' необходимо выбрать значение из списка перечислений изображений."
            )
        # параметр является целочисленным перечислением
        elif self.par.parametr_type.pk == EnumsIds.DOUBLE and (
            not self.enum_val or
            any([self.int_value, self.int_value]) or # если для параметра-перечисления целых чисел указаны значения полей int_value, double_value
            self.enum_val.enum.main_class.pk != EnumsIds.DOUBLE
        ):
            raise ValidationError(
                "Для параметра типа 'Вещественное перечисление' необходимо выбрать значение из списка вещественных перечислений."
            )
        # параметр является вещественным перечислением
        elif self.par.parametr_type.pk == EnumsIds.INT and (
            not self.enum_val or
            any([self.int_value, self.int_value]) or # если для параметра-перечисления вещественных чисел указаны значения полей int_value, double_value
            self.enum_val.enum.main_class.pk != EnumsIds.INT
        ):
            raise ValidationError(
                "Для параметра типа 'Целочисленное перечисление' необходимо выбрать значение из списка целочисленных перечислений."
            )
        # параметр является целочисленным
        elif self.par.parametr_type.pk == ParamIds.INT and (
            not self.int_value or
            any([self.enum_val, self.double_value]) # если для целочисленного параметра указаны значения полей enum_val или double_value
        ):
            raise ValidationError(
                "Для параметра типа 'Целое число' необходимо указать целочисленное значение."
            )
        # параметр является вещественным
        elif self.par.parametr_type.pk == ParamIds.DOUBLE and (
            not self.double_value or
            any([self.enum_val, self.int_value]) # если для вещественного параметра указаны значения полей enum_val или double_value
        ):
            raise ValidationError(
                "Для параметра типа 'Вещественное число' необходимо указать вещественное значение."
            )

    def _get_enum_display_value(self):
        """Возвращает строковое представление для значения перечисления в зависимости от его типа."""
        enum_type_id = self.enum_val.enum.main_class.id
        if enum_type_id == EnumsIds.STRING:  # строковое
            return self.enum_val.name
        elif enum_type_id == EnumsIds.IMAGE:  # изображение
            return self.enum_val.short_name
        elif enum_type_id == EnumsIds.DOUBLE:  # вещественное
            return f"{self.enum_val.short_name} - {self.enum_val.double_value}"
        else:  # целочисленное
            return f"{self.enum_val.short_name} - {self.enum_val.int_value}"

    def _get_enum_raw_value(self):
        """Возвращает сырое значение перечисления (для get_value)."""
        enum_type_id = self.enum_val.enum.main_class.id
        if enum_type_id == EnumsIds.STRING: # строковое
            return self.enum_val.name
        elif enum_type_id == EnumsIds.IMAGE: # изображение
            return self.enum_val.image
        elif enum_type_id == EnumsIds.DOUBLE: # вещественное
            return self.enum_val.double_value
        else: # целочисленное
            return self.enum_val.int_value

    def __str__(self):
        if self.enum_val:
            return f"{self.prod.name} - {self._get_enum_display_value()}"
        elif self.int_value is not None:
            return f"{self.prod.name} - {self.par.name} - {self.int_value}"
        else:
            return f"{self.prod.name} - {self.par.name} - {self.double_value}"


    @property
    def value(self):
        if self.int_value is not None:
            return self.int_value
        elif self.double_value is not None:
            return self.double_value
        elif self.enum_val:
            return self._get_enum_raw_value()
        else:
            return None
