from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
    CreateView,
)

from core.mixins import CommonContextMixin, HandbookExecutiveRequiredMixin

from ei.models import Ei
from ei.constants import EiConsts
from ei.forms import EiForm


class EiListView(
    PermissionRequiredMixin,
    CommonContextMixin,
    ListView
):
    paginate_by = EiConsts.PER_PAGE
    permission_required = "ei.view_ei"
    template_name = "ei/list.html"
    context_object_name = "eis"

    def get_queryset(self):
        query = self.request.GET.get("query")
        if not query:
            return (
                Ei.objects.all().order_by("id")
            )
        return (
            Ei.objects.filter(name__icontains=query).order_by("id")
        )


class EiDetailView(
    PermissionRequiredMixin,
    CommonContextMixin,
    DetailView
):
    permission_required = "ei.view_ei"
    model = Ei
    context_object_name = "ei"
    template_name = "ei/detail.html"
    pk_url_kwarg = "ei_id"


class EiCreateUpdateDeleteMixin(HandbookExecutiveRequiredMixin):
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
