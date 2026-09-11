from django.contrib.admin import ModelAdmin, register

from accounts.models import Role


@register(Role)
class RoleAdmin(ModelAdmin):
    ordering = ("name",)
    list_display = (
        "code",
        "name",
        "group",
    )
    list_filter = (
        "code",
        "name",
    )
    search_fields = (
        "code",
        "name",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "code",
                    "name",
                    "description",
                    "group",
                    "is_self_registerable",
                )
            }
        ),
    )
