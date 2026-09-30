from django.db import connection
from django.db.models import QuerySet, Q

from core.queries import ClassStructQueries

from classes.constants import ProductsConsts, ENUMS_IDS, EnumsIds, ParamIds, MetaConsts
from classes.models import ClassStruct as Classificator, ParClass


class ClassificatorSelector:
    @staticmethod
    def products() -> QuerySet:
        """Returns QuerySet of products classes"""
        with connection.cursor() as cursor:
            cursor.execute(ClassStructQueries.FIND_GR_GR, [ProductsConsts.PRODUCT_ID])
            data = cursor.fetchall()
            prod_classes_ids = [element[0] for element in data]
        return Classificator.objects.filter(id__in=prod_classes_ids)

    @staticmethod
    def terminal_product_classes() -> QuerySet[Classificator]:
        """Returns QuerySet of terminal products classes"""
        with connection.cursor() as cursor:
            cursor.execute(ClassStructQueries.FIND_GR_GR, [ProductsConsts.PRODUCT_ID])
            terminal_classes = cursor.fetchall()
            terminal_classes_ids = [element[0] for element in terminal_classes]
        return Classificator.objects.filter(id__in=terminal_classes_ids)

    @staticmethod
    def terminal_enum_classes() -> QuerySet:
        """Returns QuerySet of terminal enum classes"""
        with connection.cursor() as cursor:
            cursor.execute(ClassStructQueries.GET_TERMINAL_CLASSES, [EnumsIds.PARENT])
            terminal_enum_classes = cursor.fetchall()
            terminal_enum_classes_ids = [
                element[0] for element in terminal_enum_classes
            ]
            terminal_enum_classes_ids.extend(ENUMS_IDS)
            ids = set(terminal_enum_classes_ids)
            ids = ids.difference(ENUMS_IDS)
        return Classificator.objects.filter(id__in=ids)

    @staticmethod
    def parametr_types() -> QuerySet:
        """Returns QuerySet of parametr types"""
        string_enum = Classificator.objects.filter(pk=EnumsIds.STRING)
        image_enum = Classificator.objects.filter(pk=EnumsIds.IMAGE)
        num_enums = Classificator.objects.filter(main_class__exact=EnumsIds.NUMERIC)
        num_params = Classificator.objects.filter(main_class__exact=ParamIds.NUMERIC)
        agregat_type = Classificator.objects.filter(pk__in=[ParamIds.AGREGAT])
        result_queryset = (
            string_enum | image_enum | num_params | num_enums | agregat_type
        )
        return result_queryset

    @staticmethod
    def enum_classes() -> QuerySet:
        """Returns QuerySet of enum classes"""
        string_enum = Classificator.objects.filter(pk=EnumsIds.STRING)
        image_enum = Classificator.objects.filter(pk=EnumsIds.IMAGE)
        num_enums = Classificator.objects.filter(main_class__exact=EnumsIds.NUMERIC)
        return string_enum | image_enum | num_enums

    @staticmethod
    def all_enum_classes() -> QuerySet:
        """Returns QuerySet of all enum classes"""
        with connection.cursor() as cursor:
            cursor.execute(ClassStructQueries.FIND_GR_GR, [EnumsIds.NUMERIC])
            classes_ids = cursor.fetchall()
            classes_ids = [element[0] for element in classes_ids]
        return Classificator.objects.filter(id__in=classes_ids)

    @staticmethod
    def operations():
        operations = Classificator.objects.filter(
            Q(main_class__exact=MetaConsts.TECH_OPERATION)
            | Q(pk__exact=MetaConsts.OPERATION)
            | Q(main_class__exact=MetaConsts.OPERATION)
        )
        return operations

    @staticmethod
    def technological_operations():
        operations = Classificator.objects.filter(
            main_class__exact=MetaConsts.TECH_OPERATION
        )
        return operations

    @staticmethod
    def professions():
        professions = Classificator.objects.filter(
            main_class__exact=MetaConsts.PROFESSION
        )
        return professions

    @staticmethod
    def qualifications():
        qualifications = Classificator.objects.filter(
            main_class__exact=MetaConsts.QUALIFICATION
        )
        return qualifications

    @staticmethod
    def economic_activity_subjects():
        subjects = Classificator.objects.filter(
            main_class__exact=MetaConsts.ECONOMIC_ACTIVITY_SUBJECT
        )
        return subjects

    @staticmethod
    def means_of_labor():
        means_of_labor = Classificator.objects.filter(
            main_class__exact=MetaConsts.MEANS_OF_LABOR
        )
        return means_of_labor

    @staticmethod
    def category_classes_list(cls_):
        return (
            Classificator.objects.filter(main_class=cls_)
            .select_related("main_class")
            .order_by("id")
        )

    @staticmethod
    def fetch_detail_info(class_id: int):
        return (
            Classificator.objects.filter(pk=class_id).select_related("main_class").first()
        )


class ParClassSelector:
    @staticmethod
    def fetch_parclass_list(class_id: int):
        return (
            ParClass.objects.filter(class_field=class_id)
            .select_related("parametr__par_ei", "parametr__parametr_type")
            .order_by("num")
        )

    @staticmethod
    def fetch_by_ids(class_id: int, param_id: int):
        return ParClass.objects.get(
            class_field=class_id,
            parametr=param_id,
        )
