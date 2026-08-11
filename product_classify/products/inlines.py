from django.contrib import admin

from products.models import ParProd
from products.constants import ParProdConsts


class ParProdInline(admin.TabularInline):
    model = ParProd
    extra = ParProdConsts.INLINE_EXTRA
