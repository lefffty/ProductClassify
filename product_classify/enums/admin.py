from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Enums
)


@admin.register(Enums)
class EnumsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'enum',
        'num',
        'name',
        'short_name',
        'double_value',
        'int_value',
        'image_value',
    )
    fieldsets = (
        (None, {
            'fields': (
                'enum',
                'num',
                'name',
                'short_name',
                'double_value',
                'int_value',
                'image_value',
                'display_image_value',
            )
        }),
    )
    readonly_fields = (
        'display_image_value',
    )

    @admin.display(description='Изображение')
    @mark_safe
    def display_image_value(self, obj):
        if obj.image_value:
            return (f'<a href="{obj.image_value.url}" target="_blank"><img '
                    f'src="{obj.image_value.url}" style="max-height:100px;"></a>')
        return '-'
