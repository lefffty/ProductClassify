from django.contrib.admin import ModelAdmin, register

from route_tech.models import (
    EconomicActivitySubject,
    GroupWorkingCenter,
    ProdOperation,
)


@register(EconomicActivitySubject)
class EconomicActivitySubjectAdmin(ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "main_class",
        "main_subject",
    )
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
