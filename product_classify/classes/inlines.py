from django.contrib import admin

from classes.models import ParClass
from classes.constants import ParClassConsts


class ParClassTabularInline(admin.TabularInline):
    model = ParClass
    extra = ParClassConsts.INLINE_EXTRA
