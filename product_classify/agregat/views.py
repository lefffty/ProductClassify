from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    FormView,
    ListView,
    DetailView,
    DeleteView,
    CreateView,
)

from parametr.models import Parametr

from core.mixins import CommonContextMixin, HandbookExecutiveRequiredMixin

from agregat.models import Agregat
from agregat.selectors import AgregatSelector
from agregat.forms import AgregatForm, ChangeAgregatNumForm


class AgregatListView(
    PermissionRequiredMixin,
    CommonContextMixin,
    ListView,
):
    permission_required = "agregat.view_agregat"
    template_name = "agregat/list.html"
    context_object_name = "agregats"

    def get_queryset(self):
        query = self.request.GET.get("query")
        if not query:
            return AgregatSelector.fetch_all()
        return AgregatSelector.search_by_name(query)


class AgregatDetailView(
    PermissionRequiredMixin,
    CommonContextMixin,
    DetailView,
):
    permission_required = "agregat.view_agregat"
    template_name = "agregat/detail.html"
    pk_url_kwarg = "agregat_id"
    context_object_name = "agregat"

    def get_object(self):
        agregat_id = self.kwargs.get("agregat_id")
        return AgregatSelector.fetch_by_id(agregat_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agregat_id = self.kwargs.get("agregat_id")
        context["agr_parametrs"] = AgregatSelector.agregat_params_list(agregat_id)
        return context


class AgregatParametrCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    CreateView,
):
    form_class = AgregatForm
    model = Agregat
    template_name = "agregat/agregat.html"

    def get_success_url(self):
        agregat_id = self.kwargs.get("agregat_id")
        return reverse_lazy(
            "agregat:detail",
            kwargs={
                "agregat_id": agregat_id,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agregat_id = self.kwargs.get("agregat_id")
        context["instance"] = AgregatSelector.fetch_by_id(agregat_id)
        return context


class AgregatParametrDeleteView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    DeleteView,
):
    model = Agregat
    template_name = "agregat/agregat.html"
    context_object_name = "instance"

    def get_object(self):
        agregat_id = self.kwargs.get("agregat_id")
        param_id = self.kwargs.get("param_id")
        return AgregatSelector.fetch_agregat_parametr(agregat_id, param_id)

    def get_success_url(self):
        agregat_id = self.kwargs.get("agregat_id")
        return reverse_lazy(
            "agregat:detail",
            kwargs={
                "agregat_id": agregat_id,
            },
        )


class ChangeAgregatNumView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    FormView
):
    model = Agregat
    template_name = "agregat/change_agr_num.html"
    form_class = ChangeAgregatNumForm

    def get_agregat(self):
        if not hasattr(self, "_agregat"):
            self._agregat = get_object_or_404(Parametr, pk=self.kwargs["agregat_id"])
        return self._agregat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance"] = self.get_agregat()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["agr"] = self.get_agregat()
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            "agregat:detail", kwargs={"agregat_id": self.kwargs.get("agregat_id")}
        )
