from django.contrib import admin

from .models import (
    Agregat,
)


@admin.register(Agregat)
class AgregatAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'agr',
        'par',
        'num',
    )
    fieldsets = (
        (None, {
            'fields': (
                'agr',
                'par',
                'num',
            )
        }),
    )
