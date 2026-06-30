from django.views.generic.base import ContextMixin

from classes.models import ClassStruct
from classes.constants import FASTENER_ID


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(main_class__exact=FASTENER_ID)
        context["fastener_classes"] = fastener_classes
        return context