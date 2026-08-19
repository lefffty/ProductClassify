from django.core.exceptions import ValidationError
from django.db import models

from classes.models import ClassStruct
from classes.constants import EnumsIds, ENUMS_IDS

from enums.constants import EnumsConsts
from enums.errors import StringEnumErrors, ImageEnumErrors, IntEnumErrors, DoubleEnumErrors, EnumsErrors


class Enums(models.Model):
    enum = models.ForeignKey(
        ClassStruct,
        verbose_name="Родительский класс",
        on_delete=models.CASCADE,
        related_name="class_enum_values",
    )
    num = models.PositiveSmallIntegerField(
        verbose_name="Номер позиции в перечислении",
        null=False,
        blank=False,
    )
    name = models.CharField(
        verbose_name="Название перечисления",
        max_length=EnumsConsts.NAME_MAX_LENGTH,
        null=True,
        blank=True,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название перечисления",
        max_length=EnumsConsts.SHORT_NAME_MAX_LENGTH,
        null=True,
        blank=True,
    )
    double_value = models.FloatField(
        verbose_name="Вещественное значение перечисления",
        null=True,
        blank=True,
    )
    int_value = models.IntegerField(
        verbose_name="Целочисленное значение перечисления",
        null=True,
        blank=True,
    )
    image = models.ImageField(
        verbose_name="Изображение перечисления",
        upload_to="enum_images/",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Значение перечисления"
        verbose_name_plural = "Значения перечисления"
        unique_together = ("enum", "num")

    @classmethod
    def image_nums(cls):
        return cls.objects.filter(enum__main_class__id=EnumsIds.IMAGE)

    @classmethod
    def string_nums(cls):
        return cls.objects.filter(enum__main_class__id=EnumsIds.STRING)

    @classmethod
    def int_nums(cls):
        return cls.objects.filter(enum__main_class__id=EnumsIds.INT)

    @classmethod
    def double_nums(cls):
        return cls.objects.filter(enum__main_class__id=EnumsIds.DOUBLE)

    @property
    def value(self):
        enum_type = self.enum.main_class.pk
        if enum_type == EnumsIds.STRING:
            return self.name
        elif enum_type == EnumsIds.IMAGE:
            return self.image
        elif enum_type == EnumsIds.INT:
            return self.int_value
        elif enum_type == EnumsIds.DOUBLE:
            return self.double_value

    def clean(self):
        try:
            enum = self.enum
        except self.__class__.enum.RelatedObjectDoesNotExist:
            return

        if self.enum.main_class.pk not in ENUMS_IDS:
            raise ValidationError(EnumsErrors.INVALID_PARENT)

        if self.enum.main_class.pk == EnumsIds.IMAGE and any(
            [self.double_value, self.int_value]
        ):
            raise ValidationError(ImageEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)
        elif self.enum.main_class.pk == EnumsIds.STRING and any(
            [self.double_value, self.int_value]
        ):
            raise ValidationError(StringEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)
        elif self.enum.main_class.pk == EnumsIds.INT and any(
            [self.name, self.short_name, self.double_value, self.image]
        ):
            raise ValidationError(IntEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)
        elif self.enum.main_class.pk == EnumsIds.DOUBLE and any(
            [self.name, self.short_name, self.int_value, self.image]
        ):
            raise ValidationError(DoubleEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)

    def __str__(self):
        # если данное значение перечисления является перечислением строк или изображений
        if self.enum.main_class.id == EnumsIds.STRING or self.enum.main_class.id == EnumsIds.IMAGE:
            return self.short_name
        # если данное значение перечисления является перечислением вещественных чисел
        elif self.enum.main_class.id == EnumsIds.DOUBLE:
            return str(self.double_value)
        # если данное значение перечисления является перечислением целых чисел
        else:
            return str(self.int_value)
