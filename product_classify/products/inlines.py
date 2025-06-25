from django.contrib import admin

from .models import ParProd
from .constants import PARPROD_INLINE_EXTRA


class ParProdInline(admin.TabularInline):
    model = ParProd
    extra = PARPROD_INLINE_EXTRA
