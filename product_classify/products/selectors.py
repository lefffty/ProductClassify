from django.db.models import Q, Exists, OuterRef, QuerySet

from classes.models import ParClass
from classes.constants import ENUM_PARAMS, NUMERIC_PARAMS, ParamIds

from products.models import Prod, ParProd


class ProdSelector:
    @staticmethod
    def fetch_by_id(product_id: int):
        return (
            Prod.objects
            .filter(pk=product_id)
            .select_related(
                "class_field__main_class",
            )
            .first()
        )

    @staticmethod
    def fetch_detail_info(prod):
        return (
            ParProd.objects
            .filter(prod=prod)
            .select_related(
                "par",
                "enum_val__enum__main_class",
            )
        )

    @staticmethod
    def fetch_base_queryset(class_id: int):
        return (
            Prod.objects
            .filter(class_field_id=class_id)
            .select_related("class_field")
        )

    @staticmethod
    def get_filtered_products(
        products_qs: QuerySet[Prod], form_data: dict, class_id: int
    ):
        par_classes = ParClass.objects.filter(class_field=class_id).select_related(
            "parametr__parametr_type"
        )
        conditions = []

        for par_class in par_classes:
            param_name = par_class.parametr.name
            value = form_data.get(param_name)
            if param_name in form_data and value:
                param_type_id = par_class.parametr.parametr_type.id

                if param_type_id in ENUM_PARAMS:
                    condition = Q(par=par_class.parametr, enum_val=value)
                elif param_type_id in NUMERIC_PARAMS:
                    mn_val, mx_val = value
                    if mn_val and mx_val:
                        try:
                            if param_type_id == ParamIds.DOUBLE:
                                mn_val, mx_val = float(mn_val), float(mx_val)
                                condition = Q(
                                    par=par_class.parametr,
                                    double_value__gte=mn_val,
                                    double_value__lte=mx_val,
                                )
                            elif param_type_id == ParamIds.INT:
                                mn_val, mx_val = int(mn_val), int(mx_val)
                                condition = Q(
                                    par=par_class.parametr,
                                    int_value__gte=mn_val,
                                    int_value__lte=mx_val,
                                )
                        except (ValueError, TypeError) as e:
                            print("CAUGHT CONVERSION ERROR:", e)
                else:
                    continue

                conditions.append(
                    Exists(ParProd.objects.filter(prod=OuterRef("pk")).filter(condition))
                )

        for cond in conditions:
            products_qs = products_qs.filter(cond)

        return products_qs

    @staticmethod
    def annotate_filtered_products(
        base_qs: QuerySet
    ):
        return base_qs.annotate(
            has_params=Exists(ParProd.objects.filter(prod=OuterRef("pk")))
        ).filter(has_params=False)



class ParProdSelector:
    @staticmethod
    def fetch_object_by_ids(prod_id: int, param_id: int):
        return ParProd.objects.get(
            prod=prod_id,
            par=param_id,
        )
