from django.contrib.admin import ModelAdmin, register

from route_tech.models import (
    EconomicActivitySubject,
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
