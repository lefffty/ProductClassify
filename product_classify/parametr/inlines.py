from django.contrib import admin

from agregat.models import Agregat
from .constants import AGR_INLINE_EXTRA


class AgregatInline(admin.TabularInline):
    model = Agregat
    extra = AGR_INLINE_EXTRA
    fk_name = 'agr'
