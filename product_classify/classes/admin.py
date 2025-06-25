from django.contrib import admin

from .models import (
    ClassStruct
)


@admin.register(ClassStruct)
class ClassStructAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'short_name',
        'base_ei',
        'main_class',
    )
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'short_name',
                'base_ei',
                'main_class',
            )
        }),
    )
