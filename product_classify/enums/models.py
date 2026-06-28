from django.db import models

from classes.models import (
    ClassStruct,
)

from .constants import (
    ENUMS_NAME_MAX_LENGTH,
    ENUMS_SHORT_NAME_MAX_LENGTH,
    IMAGE_ENUMS_ID,
    STRING_ENUMS_ID,
    INT_ENUMS_ID,
    DOUBLE_ENUMS_ID,
)


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
        max_length=ENUMS_NAME_MAX_LENGTH,
        null=True,
    )
    short_name = models.CharField(
        verbose_name="Сокращенное название перечисления",
        max_length=ENUMS_SHORT_NAME_MAX_LENGTH,
        null=True,
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
        blank=False,
    )

    class Meta:
        verbose_name = "Значение перечисления"
        verbose_name_plural = "Значения перечисления"
        unique_together = ("enum", "num")

    @classmethod
    def image_nums(cls):
        return cls.objects.filter(enum__main_class__id=IMAGE_ENUMS_ID)

    @classmethod
    def string_nums(cls):
        return cls.objects.filter(enum__main_class__id=STRING_ENUMS_ID)

    @classmethod
    def int_nums(cls):
        return cls.objects.filter(enum__main_class__id=INT_ENUMS_ID)

    @classmethod
    def double_nums(cls):
        return cls.objects.filter(enum__main_class__id=DOUBLE_ENUMS_ID)

    def __str__(self):
        # если данное значение перечисления является перечислением строк или изображений
        if self.enum.main_class.id == 15 or self.enum.main_class.id == 16:
            return self.short_name
        # если данное значение перечисления является перечислением вещественных чисел
        elif self.enum.main_class.id == 18:
            return self.short_name + " - " + str(self.double_value)
        # если данное значение перечисления является перечислением целых чисел
        else:
            return self.short_name + " - " + str(self.int_value)
