from django.contrib.admin import ModelAdmin, register

from accounts.models import Role, User


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
            },
        ),
    )


@register(User)
class UserAdmin(ModelAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "middle_name",
        "phone_number",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "last_name", "first_name", "phone_number")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {"fields": ("last_name", "first_name", "middle_name", "phone_number")},
        ),
        (
            "Роль и права",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Даты", {"fields": ("last_login",)}),
    )
