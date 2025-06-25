from django.contrib import admin

from .models import (
    Prod,
    ParProd
)


@admin.register(Prod)
class ProdAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'short_name',
        'class_id',
        'image',
    )
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'short_name',
                'class_id',
                'image',
            )
        }),
    )


@admin.register(ParProd)
class ParProdAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'prod',
        'par',
        'int_value',
        'double_value',
        'enum_val',
    )
    fieldsets = (
        (None, {
            'fields': (
                'prod',
                'par',
                'int_value',
                'double_value',
                'enum_val',
            )
        }),
    )