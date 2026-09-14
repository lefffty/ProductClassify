from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (
    ListView,
    DeleteView,
    DetailView,
    CreateView,
    UpdateView,
)

from classes.constants import ParamIds

from core.mixins import CommonContextMixin, HandbookExecutiveRequiredMixin

from parametr.models import Parametr
from parametr.forms import ParametrForm


class ParametrListView(
    PermissionRequiredMixin,
    CommonContextMixin,
    ListView,
):
    permission_required = "parametr.view_parametr"
    template_name = "parametr/list.html"
    context_object_name = "parameters"
    ordering = "id"

    def get_queryset(self):
        parameters = Parametr.objects.exclude(
            parametr_type__exact=ParamIds.AGREGAT
        ).select_related("parametr_type")
        return parameters


class ParametrDetailView(
    PermissionRequiredMixin,
    CommonContextMixin,
    DetailView,
):
    permission_required = "parametr.view_parametr"
    model = Parametr
    template_name = "parametr/detail.html"
    pk_url_kwarg = "parametr_id"
    context_object_name = "parameter"


class ParametrCreateUpdateDeleteMixin(
    HandbookExecutiveRequiredMixin
):
    model = Parametr
    template_name = "parametr/parametr.html"


class ParametrCreateView(
    ParametrCreateUpdateDeleteMixin,
    CommonContextMixin,
    CreateView,
):
    form_class = ParametrForm
    success_url = reverse_lazy("parametr:list")


class ParametrUpdateView(
    ParametrCreateUpdateDeleteMixin,
    CommonContextMixin,
    UpdateView,
):
    form_class = ParametrForm
    pk_url_kwarg = "parametr_id"

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy(
            "parametr:detail",
            kwargs={
                "parametr_id": pk,
            },
        )


class ParametrDeleteView(
    ParametrCreateUpdateDeleteMixin,
    CommonContextMixin,
    DeleteView,
):
    success_url = reverse_lazy("parametr:list")
    pk_url_kwarg = "parametr_id"
    context_object_name = "instance"
