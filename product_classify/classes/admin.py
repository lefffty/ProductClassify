from django.contrib import admin

from .models import (
    ClassStruct,
    ParClass,
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


@admin.register(ParClass)
class ParClassAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'class_field',
        'parametr',
        'num',
        'min_value',
        'max_value',
    )
    fieldsets = (
        (None, {
            'fields': (
                'class_field',
                'parametr',
                'num',
                'min_value',
                'max_value',
            )
        }),
    )
