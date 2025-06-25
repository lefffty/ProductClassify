from django.contrib import admin

from .models import (
    Ei
)


@admin.register(Ei)
class EiAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'short_name',
        'code',
        'convert_factor',
        'main_class',
    )
    ordering = (
        'code',
    )
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'short_name',
                'code',
                'convert_factor',
                'main_class',
            )
        }),
    )
