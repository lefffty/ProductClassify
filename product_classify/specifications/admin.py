from django.contrib import admin

from specifications.models import ProdComponent, SpecificationLogs


@admin.register(ProdComponent)
class ProdComponentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "parent_prod",
        "component",
        "num",
        "quantity",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "parent_prod",
                    "component",
                    "num",
                    "quantity",
                )
            }
        ),
    )


@admin.register(SpecificationLogs)
class SpecificationLogsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "pair",
        "updated_at",
        "old_quantity",
        "new_quantity",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "pair",
                    "old_quantity",
                    "new_quantity",
                ),
            }
        ),
    )
    readonly_fields = (
        "updated_at",
    )
