from django.db.models import Q, Exists, OuterRef, QuerySet

from classes.models import ParClass
from classes.constants import ENUM_PARAMS, NUMERIC_PARAMS, ParamIds

from products.models import ParProd, Prod


def get_filtered_products(products_qs: QuerySet[Prod], form_data: dict, class_id: int) -> QuerySet:
    par_classes = ParClass.objects.filter(class_field=class_id).select_related(
        'parametr__parametr_type'
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
                                double_value__lte=mx_val
                            )
                        elif param_type_id == ParamIds.INT:
                            mn_val, mx_val = int(mn_val), int(mx_val)
                            condition = Q(
                                par=par_class.parametr,
                                int_value__gte=mn_val,
                                int_value__lte=mx_val
                            )
                    except (ValueError, TypeError) as e:
                        print("CAUGHT CONVERSION ERROR:", e)
            else:
                continue

            conditions.append(
                Exists(ParProd.objects.filter(prod=OuterRef('pk')).filter(condition))
            )

    for cond in conditions:
        products_qs = products_qs.filter(cond)

    return products_qs
