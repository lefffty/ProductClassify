from django.db import models, connection

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
from ei.models import (
    Ei,
)


class TerminalProdClassesManager(models.Manager):
    def get_queryset(self):
        terminal_classes_ids = None
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM get_terminal_classes({FASTENER_ID});')
            terminal_classes = cursor.fetchall()
            terminal_classes_ids = [element[0] for element in terminal_classes]
        return super().get_queryset().filter(id__in=terminal_classes_ids)


class TerminalEnumClasses(models.Manager):
    def get_queryset(self):
        terminal_enum_classes_ids = None
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM get_terminal_classes({ENUM_PARENT_NODE_ID});'
            )
            terminal_enum_classes = cursor.fetchall()
            terminal_enum_classes_ids = [
                element[0] for element in terminal_enum_classes]
        return super().get_queryset().filter(
            id__in=terminal_enum_classes_ids)


class ParametrTypeClasses(models.Manager):
    def get_queryset(self):
        string_enum = ClassStruct.objects.filter(pk=ENUM_CLASSES_IDS[0])
        image_enum = ClassStruct.objects.filter(pk=ENUM_CLASSES_IDS[1])
        num_enums = ClassStruct.objects.filter(main_class__exact=NUM_ENUM_ID)
        num_params = ClassStruct.objects.filter(main_class__exact=NUM_PARAM_ID)
        result_queryset = string_enum | image_enum | num_params | num_enums
        return result_queryset


class AllEnumClasses(models.Manager):
    def get_queryset(self):
        classes_ids = None
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM find_gr_gr({ENUM_PARENT_NODE_ID});'
            )
            classes_ids = cursor.fetchall()
            classes_ids = [
                element[0] for element in classes_ids]
        return super().get_queryset().filter(
            id__in=classes_ids
        )


class EnumClasses(models.Manager):
    def get_queryset(self):
        string_enum = ClassStruct.objects.filter(pk=ENUM_CLASSES_IDS[0])
        image_enum = ClassStruct.objects.filter(pk=ENUM_CLASSES_IDS[1])
        num_enums = ClassStruct.objects.filter(main_class__exact=NUM_ENUM_ID)
        return string_enum | image_enum | num_enums


class ProdClasses(models.Manager):
    def get_queryset(self):
        prod_classes_ids = None
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM find_gr_gr({PRODUCT_ID});')
            data = cursor.fetchall()
            prod_classes_ids = [
                element[0] for element in data
            ]
        return super().get_queryset().filter(
            id__in=prod_classes_ids
        )


class ClassStruct(models.Model):
    name = models.CharField(
        verbose_name='Название класса',
        blank=False,
        null=False,
        max_length=CLASS_STRUCT_NAME_MAX_LENGTH,
    )
    short_name = models.CharField(
        verbose_name='Сокращенное название класса',
        blank=True,
        null=True,
        max_length=CLASS_STRUCT_SHORT_NAME_MAX_LENGTH,
    )
    base_ei = models.ForeignKey(
        Ei,
        verbose_name='Базовая единица измерения',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    main_class = models.ForeignKey(
        'self',
        verbose_name='Родительский класс',
        null=True,
        blank=False,
        on_delete=models.CASCADE
    )

    objects = models.Manager()

    terminal_product_classes = TerminalProdClassesManager()
    terminal_enum_classes = TerminalEnumClasses()
    parametr_types = ParametrTypeClasses()
    products = ProdClasses()
    enum_classes = EnumClasses()
    all_enum_classes = AllEnumClasses()

    class Meta:
        verbose_name = 'Классификатор'
        verbose_name_plural = 'Классификатор'

    def __str__(self):
        return self.name


class ParClass(models.Model):
    class_field = models.ForeignKey(
        ClassStruct,
        verbose_name='Класс',
        on_delete=models.DO_NOTHING,
        related_name='class_params'
    )
    parametr = models.ForeignKey(
        'parametr.Parametr',
        verbose_name='Параметр',
        on_delete=models.DO_NOTHING,
    )
    num = models.PositiveSmallIntegerField(
        verbose_name='Позиция в списке параметров класса',
        null=False,
        blank=False,
    )
    min_value = models.FloatField(
        verbose_name='Минимальное значение параметра',
        null=True,
        blank=True,
    )
    max_value = models.FloatField(
        verbose_name='Максимальное значение параметра',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Параметр класса'
        verbose_name_plural = 'Параметры класса'
        constraints = [
            models.UniqueConstraint(
                fields=['class_field', 'parametr'],
                name='%(class)s_pk'
            )
        ]

    def __str__(self):
        return f'{self.class_field.name} - {self.parametr.name}'
