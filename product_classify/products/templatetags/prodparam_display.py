from django import template
from django.urls import reverse
from django.utils.html import format_html

from products.models import ParProd
from classes.constants import EnumsIds


register = template.Library()


@register.simple_tag
def render_param_value(param: ParProd):
    """Рендерит значение ParProd: картинку для image-перечисления, иначе текст."""
    if (
        param.enum_val
        and param.enum_val.enum.main_class_id == EnumsIds.IMAGE
        and param.enum_val.image
    ):
        return format_html(
            '<a href="{}" class="d-inline-block">'
            '  <img src="{}" alt="Изображение перечисления" '
            '       style="max-height: 60px; max-width: 150px; object-fit: cover;" '
            '       class="rounded">'
            '</a>',
            reverse(
                "enums:detail",
                args=[param.enum_val.enum.main_class_id, param.enum_val.id],
            ),
            param.enum_val.image.url,
        )
    return param.value if param.value is not None else "—"
