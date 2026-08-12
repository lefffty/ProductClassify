from django.core.validators import MinValueValidator
from django.db import models, connection
from django.db.models import QuerySet, Q, F
from django.forms import ValidationError

from ei.models import Ei

from core.queries import ClassStructQueries

from classes.constants import (
    EnumsIds,
    ClassStructConsts,
    ParClassConsts,
    ProductsConsts,
    ParamIds,
    ENUMS_IDS
)
from classes.errors import ParClassErrors


class ClassStruct(models.Model):
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

    def __str__(self):
        return self.name

    @classmethod
    def products(cls) -> QuerySet:
        """Returns QuerySet of products classes"""
        with connection.cursor() as cursor:
            cursor.execute(ClassStructQueries.FIND_GR_GR, [ProductsConsts.PRODUCT_ID])
            data = cursor.fetchall()
            prod_classes_ids = [element[0] for element in data]
        return cls.objects.filter(id__in=prod_classes_ids)

    @classmethod
    def terminal_product_classes(cls) -> QuerySet[ClassStruct]:
        """Returns QuerySet of terminal products classes"""
        with connection.cursor() as cursor:
            cursor.execute(ClassStructQueries.FIND_GR_GR, [ProductsConsts.PRODUCT_ID])
            terminal_classes = cursor.fetchall()
            terminal_classes_ids = [element[0] for element in terminal_classes]
        return cls.objects.filter(id__in=terminal_classes_ids)

    @classmethod
    def terminal_enum_classes(cls) -> QuerySet:
        """Returns QuerySet of terminal enum classes"""
        with connection.cursor() as cursor:
            cursor.execute(
                ClassStructQueries.GET_TERMINAL_CLASSES, [EnumsIds.PARENT]
            )
            terminal_enum_classes = cursor.fetchall()
            terminal_enum_classes_ids = [
                element[0] for element in terminal_enum_classes
            ]
            terminal_enum_classes_ids.extend(ENUMS_IDS)
            ids = set(terminal_enum_classes_ids)
            ids = ids.difference(ENUMS_IDS)
        return cls.objects.filter(id__in=ids)

    @classmethod
    def parametr_types(cls) -> QuerySet:
        """Returns QuerySet of parametr types"""
        string_enum = ClassStruct.objects.filter(pk=EnumsIds.STRING)
        image_enum = ClassStruct.objects.filter(pk=EnumsIds.IMAGE)
        num_enums = ClassStruct.objects.filter(main_class__exact=EnumsIds.NUMERIC)
        num_params = ClassStruct.objects.filter(main_class__exact=ParamIds.NUMERIC)
        agregat_type = ClassStruct.objects.filter(pk__in=[ParamIds.AGREGAT])
        result_queryset = (
            string_enum | image_enum | num_params | num_enums | agregat_type
        )
        return result_queryset

    @classmethod
    def enum_classes(cls) -> QuerySet:
        """Returns QuerySet of enum classes"""
        string_enum = ClassStruct.objects.filter(pk=EnumsIds.STRING)
        image_enum = ClassStruct.objects.filter(pk=EnumsIds.IMAGE)
        num_enums = ClassStruct.objects.filter(main_class__exact=EnumsIds.NUMERIC)
        return string_enum | image_enum | num_enums

    @classmethod
    def all_enum_classes(cls) -> QuerySet:
        """Returns QuerySet of all enum classes"""
        with connection.cursor() as cursor:
            cursor.execute(ClassStructQueries.FIND_GR_GR, [EnumsIds.NUMERIC])
            classes_ids = cursor.fetchall()
            classes_ids = [element[0] for element in classes_ids]
        return cls.objects.filter(id__in=classes_ids)

    @classmethod
    def delete_class_and_descendants(cls, class_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                ClassStructQueries.DELETE_CLASS_AND_DESCENDANTS,
                [class_id],
            )
            data = cursor.fetchone()[0]
        return data

    @classmethod
    def check_class_struct_cycles(self, cursor: object, cls_id: int, main_cls_id: int):
        cursor.execute(
            ClassStructQueries.CHECK_CYCLE,
            [cls_id, main_cls_id],
        )
        is_cycle = cursor.fetchone()[0]
        return is_cycle


class ParClass(models.Model):
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

    def clean(self):
        if not self.parametr_id:
            return

        enum_param_type_ids = list([*ENUMS_IDS, ParamIds.AGREGAT])
        if self.parametr.parametr_type.id in enum_param_type_ids and (
            self.min_value or self.max_value
        ):
            raise ValidationError(ParClassErrors.ENUM_AGGREGATE_RANGE_ERROR.format(self.parametr.name))

        if self.min_value and self.max_value:
            if self.min_value > self.max_value:
                raise ValidationError({
                    "min_value": ParClassErrors.MIN_GE_MAX,
                })

    def __str__(self):
        return f"{self.class_field.name} - {self.parametr.name}"
