from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
    CreateView,
)

from core.mixins import CommonContextMixin

from ei.models import Ei
from ei.forms import EiForm


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
    success_url = reverse_lazy("ei:list")


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
    context_object_name = "instance"


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
            "ei:detail",
            kwargs={
                "ei_id": pk,
            },
        )
