from django.contrib.admin import ModelAdmin, register

from route_tech.models import (
    EconomicActivitySubject,
    GroupWorkingCenter,
    ProdOperation,
    ProdOperationPos
)
from route_tech.forms import (
    EconomicActivitySubjectForm,
    GroupWorkingCenterForm,
    ProdOperationPosForm,
    ProdOperationForm,
)


@register(EconomicActivitySubject)
class EconomicActivitySubjectAdmin(ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "main_class",
        "main_subject",
    )
    form = EconomicActivitySubjectForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "short_name",
                    "main_class",
                    "main_subject",
                ),
            },
        ),
    )


@register(GroupWorkingCenter)
class GroupWorkingCenterAdmin(ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "main_class",
        "eas",
        "place",
    )
    form = GroupWorkingCenterForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "short_name",
                    "main_class",
                    "eas",
                    "place",
                ),
            },
        ),
    )


@register(ProdOperation)
class ProdOperationAdmin(ModelAdmin):
    list_display = (
        "prod",
        "tech_oper",
        "profession",
        "center",
        "qualification",
        "num_of_workers",
        "t_pz",
        "t_sht",
    )
    form = ProdOperationForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "prod",
                    "tech_oper",
                    "profession",
                    "center",
                    "qualification",
                    "num_of_workers",
                    "t_pz",
                    "t_sht",
                ),
            },
        ),
    )


@register(ProdOperationPos)
class ProdOperationPos(ModelAdmin):
    list_display = (
        "input_prod_oper",
        "output_prod_oper",
        "input_quantity",
        "output_quantity",
    )
    form = ProdOperationPosForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "input_prod_oper",
                    "output_prod_oper",
                    "input_quantity",
                    "output_quantity",
                ),
            },
        ),
    )
