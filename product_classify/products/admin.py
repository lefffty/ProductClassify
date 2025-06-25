from django.contrib import admin

from .models import (
    Prod
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