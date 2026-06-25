from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
    CreateView,
)

from product_classify.classes.models import (
    ClassStruct,
)

from .models import Ei
from .forms import EiForm
from .constants import (
    FASTENER_ID,
)


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(main_class__exact=FASTENER_ID)
        context["fastener_classes"] = fastener_classes
        return context


class EiListView(CommonContextMixin, ListView):
    model = Ei
    template_name = "ei/list.html"
    ordering = "id"
    context_object_name = "eis"


class EiDetailView(CommonContextMixin, DetailView):
    model = Ei
    context_object_name = "ei"
    template_name = "ei/detail.html"
    pk_url_kwarg = "ei_id"


class EiCreateUpdateDeleteMixin:
    template_name = "ei/ei.html"
    model = Ei
    success_url = reverse_lazy("ei:ei_list")


class EiCreateView(
    CommonContextMixin,
    EiCreateUpdateDeleteMixin,
    CreateView,
):
    form_class = EiForm
    pk_url_kwarg = "ei_id"


class EiDeleteView(
    EiCreateUpdateDeleteMixin,
    CommonContextMixin,
    DeleteView,
):
    pk_url_kwarg = "ei_id"


class EiUpdateView(
    EiCreateUpdateDeleteMixin,
    CommonContextMixin,
    UpdateView,
):
    form_class = EiForm
    pk_url_kwarg = "ei_id"

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy(
            "ei:ei_detail",
            kwargs={
                "ei_id": pk,
            },
        )
