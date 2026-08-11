from django.contrib import admin

from agregat.models import Agregat

from parametr.constants import AgrConsts


class AgregatInline(admin.TabularInline):
    model = Agregat
    extra = AgrConsts.INLINE_EXTRA
    fk_name = "agr"
