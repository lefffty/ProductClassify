from django.contrib import admin

from .models import ParClass
from .constants import PARCLASS_INLINE_EXTRA


class ParClassTabularInline(admin.TabularInline):
    model = ParClass
    extra = PARCLASS_INLINE_EXTRA
