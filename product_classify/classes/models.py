from django.core.validators import MinValueValidator
from django.db import models, connection
from django.db.models import QuerySet, Q, F
from django.forms import ValidationError

from ei.models import Ei

from .constants import (
    CLASS_STRUCT_SHORT_NAME_MAX_LENGTH,
    CLASS_STRUCT_NAME_MAX_LENGTH,
    ENUM_PARENT_NODE_ID,
    ENUM_CLASSES_IDS,
    NUM_PARAM_ID,
    FASTENER_ID,
    NUM_ENUM_ID,
    PRODUCT_ID,
)


class ClassStruct(models.Model):
    name = models.CharField(
        verbose_name="Название класса",
        null=False,
        blank=False,
        max_length=CLASS_STRUCT_NAME_MAX_LENGTH,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название класса",
        null=False,
        blank=True,
        max_length=CLASS_STRUCT_SHORT_NAME_MAX_LENGTH,
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
            cursor.execute(f"SELECT * FROM find_gr_gr({PRODUCT_ID});")
            data = cursor.fetchall()
            prod_classes_ids = [element[0] for element in data]
        return cls.objects.filter(id__in=prod_classes_ids)

    @classmethod
    def terminal_product_classes(cls) -> QuerySet:
        """Returns QuerySet of terminal products classes"""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM get_terminal_classes({FASTENER_ID});")
            terminal_classes = cursor.fetchall()
            terminal_classes_ids = [element[0] for element in terminal_classes]
        return cls.objects.filter(id__in=terminal_classes_ids)

    @classmethod
    def terminal_enum_classes(cls) -> QuerySet:
        """Returns QuerySet of terminal enum classes"""
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM get_terminal_classes({ENUM_PARENT_NODE_ID});"
            )
            terminal_enum_classes = cursor.fetchall()
            terminal_enum_classes_ids = [
                element[0] for element in terminal_enum_classes
            ]
        return cls.objects.filter(id__in=terminal_enum_classes_ids)

    @classmethod
    def parametr_types(cls) -> QuerySet:
        """Returns QuerySet of parametr types"""
        string_enum = ClassStruct.objects.filter(pk=ENUM_CLASSES_IDS[0])
        image_enum = ClassStruct.objects.filter(pk=ENUM_CLASSES_IDS[1])
        num_enums = ClassStruct.objects.filter(main_class__exact=NUM_ENUM_ID)
        num_params = ClassStruct.objects.filter(main_class__exact=NUM_PARAM_ID)
        result_queryset = string_enum | image_enum | num_params | num_enums
        return result_queryset

    @classmethod
    def enum_classes(cls) -> QuerySet:
        """Returns QuerySet of enum classes"""
        string_enum = ClassStruct.objects.filter(pk=ENUM_CLASSES_IDS[0])
        image_enum = ClassStruct.objects.filter(pk=ENUM_CLASSES_IDS[1])
        num_enums = ClassStruct.objects.filter(main_class__exact=NUM_ENUM_ID)
        return string_enum | image_enum | num_enums

    @classmethod
    def all_enum_classes(cls) -> QuerySet:
        """Returns QuerySet of all enum classes"""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM find_gr_gr({ENUM_PARENT_NODE_ID});")
            classes_ids = cursor.fetchall()
            classes_ids = [element[0] for element in classes_ids]
        return cls.objects.filter(id__in=classes_ids)


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
        validators=[MinValueValidator(1)],
    )
    min_value = models.FloatField(
        verbose_name="Минимальное значение параметра",
        null=False,
        blank=True,
    )
    max_value = models.FloatField(
        verbose_name="Максимальное значение параметра",
        null=False,
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
        if self.min_value > self.max_value:
            raise ValidationError(
                {
                    "min_value": "Minimum value should be less than maximum value",
                    "max_value": "Maximum value should be greater than minimum value",
                }
            )

    def __str__(self):
        return f"{self.class_field.name} - {self.parametr.name}"
