from django.contrib import admin

from .models import (
    Parametr
)


@admin.register(Parametr)
class ParametrAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'short_name',
        'parametr_type',
        'par_ei',
    )
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'short_name',
                'parametr_type',
                'par_ei',
            )
        }),
    )
