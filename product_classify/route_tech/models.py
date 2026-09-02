from django.db.models import (
    DecimalField,
    FloatField,
    Model,
    CharField,
    CASCADE,
    ForeignKey,
    PositiveSmallIntegerField
)
from django.core.validators import MinValueValidator

from products.models import Prod
from classes.models import ClassStruct
from route_tech.constants import EASConsts, GWCConsts, ProdOperConsts, ProdOperationPosConsts


class EconomicActivitySubject(Model):
    name = CharField(
        verbose_name="Название субъекта экономической деятельности",
        max_length=EASConsts.NAME_MAX_LENGTH,
        blank=False,
        null=False,
    )
    short_name = CharField(
        verbose_name="Сокращенное название субъекта экономической деятельности",
        max_length=EASConsts.SHORT_NAME_MAX_LENGTH,
        blank=False,
        null=False,
    )
    main_class = ForeignKey(
        ClassStruct,
        on_delete=CASCADE,
        verbose_name="Ссылка на класс субъекта экономической деятельности",
        related_name="subjects_by_class",
        null=False,
    )
    main_subject = ForeignKey(
        "self",
        verbose_name="Родительский субъект экономической деятельности",
        related_name="children",
        on_delete=CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = "Субъект экономической деятельности"
        verbose_name_plural = "Субъекты экономической деятельности"

    def __str__(self):
        return self.name


class GroupWorkingCenter(Model):
    name = CharField(
        verbose_name="Название группового рабочего центра",
        max_length=GWCConsts.NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    short_name = CharField(
        verbose_name="Сокращенное название группового рабочего центра",
        max_length=GWCConsts.SHORT_NAME_MAX_LENGTH,
        null=False,
        blank=False,
    )
    main_class = ForeignKey(
        ClassStruct,
        on_delete=CASCADE,
        verbose_name="Ссылка на родительский класс",
        related_name="working_centers_by_class",
        null=False,
    )
    eas = ForeignKey(
        EconomicActivitySubject,
        on_delete=CASCADE,
        verbose_name="Ссылка на субъект экономической деятельности",
        related_name="working_centers_by_subject",
        null=False,
    )
    place = PositiveSmallIntegerField(
        verbose_name="Количество рабочих мест на групповом рабочим центре",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Групповой рабочий центр"
        verbose_name_plural = "Групповые рабочие центры"

    def __str__(self):
        return self.name


class ProdOperation(Model):
    prod = ForeignKey(
        Prod,
        on_delete=CASCADE,
        verbose_name="Изделие",
        related_name="prod_operations",
        null=False,
        blank=False,
    )
    tech_oper = ForeignKey(
        ClassStruct,
        on_delete=CASCADE,
        verbose_name="Операция",
        related_name="tech_operations",
        null=False,
        blank=False,
    )
    profession = ForeignKey(
        ClassStruct,
        on_delete=CASCADE,
        verbose_name="Профессия рабочего",
        related_name="profession_operations",
        null=False,
        blank=False,
    )
    center = ForeignKey(
        GroupWorkingCenter,
        on_delete=CASCADE,
        verbose_name="Групповой рабочий центр",
        related_name="center_operations",
        null=False,
        blank=False,
    )
    qualification = ForeignKey(
        ClassStruct,
        on_delete=CASCADE,
        verbose_name="Квалификация рабочего",
        related_name="qualification_operations",
        null=False,
        blank=False,
    )
    num_of_workers = PositiveSmallIntegerField(
        verbose_name="Количество исполнителей, занятых при выполнении операции",
        null=False,
        blank=True,
    )
    t_pz = FloatField(
        verbose_name="Норма подготовительно-заключительного времени на операцию",
        default=ProdOperConsts.T_PZ_DEFAULT,
    )
    t_sht = FloatField(
        verbose_name="Норма штучного времени на операцию",
        default=ProdOperConsts.T_SHT_DEFAULT,
    )

    class Meta:
        verbose_name = "Пара класса <Изделие-операция>"
        verbose_name_plural = "Пары класса <Изделие-операция>"

    def __str__(self):
        return f"{self.prod.name} - {self.tech_oper.name}"


class ProdOperationPos(Model):
    input_prod_oper = ForeignKey(
        ProdOperation,
        on_delete=CASCADE,
        verbose_name="Входная пара <Изделие-операция>",
        related_name="input_prod_oper_positions",
        blank=False,
        null=False,
    )
    output_prod_oper = ForeignKey(
        ProdOperation,
        on_delete=CASCADE,
        verbose_name="Выходная пара <Изделие-операция>",
        related_name="output_prod_oper_positions",
        blank=False,
        null=False,
    )
    input_quantity = DecimalField(
        verbose_name="Расход входного ресурса",
        blank=False,
        null=False,
        validators=[
            MinValueValidator(ProdOperationPosConsts.MIN_VALUE)
        ],
        max_digits=ProdOperationPosConsts.MAX_DIGITS,
        decimal_places=ProdOperationPosConsts.DECIMAL_PLACES
    )
    output_quantity = DecimalField(
        verbose_name="Количество выходного ресурса",
        blank=False,
        null=False,
        validators=[
            MinValueValidator(ProdOperationPosConsts.MIN_VALUE)
        ],
        max_digits=ProdOperationPosConsts.MAX_DIGITS,
        decimal_places=ProdOperationPosConsts.DECIMAL_PLACES
    )

    class Meta:
        verbose_name = "Позиция входного ресурса"
        verbose_name_plural = "Позиции входных ресурсов"

    def __str__(self):
        return f"<{self.input_prod_oper}> - <{self.output_prod_oper}> ({self.input_quantity} -> {self.output_quantity})"
