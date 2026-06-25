from django.contrib import admin

from .models import Parametr
from .inlines import AgregatInline


@admin.register(Parametr)
class ParametrAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "short_name",
        "parametr_type",
        "par_ei",
    )
    inlines = (AgregatInline,)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "short_name",
                    "parametr_type",
                    "par_ei",
                )
            },
        ),
    )
