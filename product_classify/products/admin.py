from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Prod,
    ParProd
)
from .inlines import ParProdInline


@admin.register(Prod)
class ProdAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'short_name',
        'class_field',
        'display_image',
    )
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'short_name',
                'class_field',
                'image',
            )
        }),
    )
    inlines = (ParProdInline,)
    readonly_fields = ('display_image',)

    @admin.display(description='Изображение')
    @mark_safe
    def display_image(self, obj):
        if obj.image:
            return (f'<a href="{obj.image.url}" target="_blank"><img '
                    f'src="{obj.image.url}" style="max-height:100px;"></a>')
        return '-'


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