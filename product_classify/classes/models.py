from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, F
from django.forms import ValidationError

from ei.models import Ei

from classes.constants import (
    ClassStructConsts,
    ParClassConsts,
    ParamIds,
    ENUMS_IDS,
    NUMERIC_PARAMS,
)
from classes.errors import ParClassErrors


class ClassStruct(models.Model):
    """Модель классификатора"""

    name = models.CharField(
        verbose_name="Название класса",
        null=False,
        blank=False,
        max_length=ClassStructConsts.NAME_MAX_LENGTH,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название класса",
        null=False,
        blank=True,
        max_length=ClassStructConsts.SHORT_NAME_MAX_LENGTH,
    )
    base_ei = models.ForeignKey(
        Ei,
        verbose_name="Базовая единица измерения",
        null=True,
        on_delete=models.CASCADE,
    )
    main_class = models.ForeignKey(
        "self",
        verbose_name="Родительский класс",
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Классификатор"
        verbose_name_plural = "Классификатор"
        permissions = [
            ("keep_account_of_means_of_labor", "Может вести учет средства труда"),
        ]

    def __str__(self):
        return self.name


class ParClass(models.Model):
    """Модель параметра класса"""

    class_field = models.ForeignKey(
        ClassStruct,
        verbose_name="Класс",
        on_delete=models.CASCADE,
        related_name="class_params",
    )
    parametr = models.ForeignKey(
        "parametr.Parametr",
        verbose_name="Параметр",
        on_delete=models.CASCADE,
    )
    num = models.PositiveSmallIntegerField(
        verbose_name="Позиция в списке параметров класса",
        null=False,
        blank=False,
        validators=[MinValueValidator(ParClassConsts.NUM_MIN_VALUE)],
    )
    min_value = models.FloatField(
        verbose_name="Минимальное значение параметра",
        null=True,
        blank=True,
    )
    max_value = models.FloatField(
        verbose_name="Максимальное значение параметра",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Параметр класса"
        verbose_name_plural = "Параметры класса"
        constraints = [
            models.UniqueConstraint(
                fields=["class_field", "parametr"],
                name="%(class)s_pk",
            ),
            models.CheckConstraint(
                check=Q(num__gt=0),
                name="%(class)s_num_gt_zero",
            ),
            models.CheckConstraint(
                check=Q(max_value__gte=F("min_value")),
                name="%(class)s_max_gte_min",
            ),
        ]

    @property
    def boundaries(self):
        parametr_type_id = self.parametr.parametr_type_id 
        if parametr_type_id in NUMERIC_PARAMS:
            return f"{self.min_value} - {self.max_value}"
        return "-"

    def clean(self):
        # если параметр не указан
        if not self.parametr_id:
            return

        # получаем списком типов перечислений + тип параметр-агрегат
        enum_param_type_ids = list([*ENUMS_IDS, ParamIds.AGREGAT])

        # проверяем, что параметр является параметром-перечислением или агрегатом и заполнены поля min_value и max_value
        # если да, то выбрасываем исключение, так как для параметра-перечисления или для параметра-агрегата нельзя задать
        # значения полей min_value или max_value
        if self.parametr.parametr_type.id in enum_param_type_ids and (
            self.min_value or self.max_value
        ):
            raise ValidationError(
                ParClassErrors.ENUM_AGGREGATE_RANGE_ERROR.format(self.parametr.name)
            )

        # если указаны поля min_value и max_value и min_value > max_value,
        # то выбрасываем исключение
        if self.min_value and self.max_value:
            if self.min_value > self.max_value:
                raise ValidationError(
                    {
                        "min_value": ParClassErrors.MIN_GE_MAX,
                    }
                )

    def delete(self, *args, **kwargs):
        from products.models import ParProd

        ParProd.objects.filter(par=self.parametr).delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.class_field.name} - {self.parametr.name}"
