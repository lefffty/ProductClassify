from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import (
    FormView,
    ListView,
    DetailView,
    DeleteView,
    CreateView,
)

from parametr.models import Parametr
from classes.constants import ParamIds
from core.mixins import CommonContextMixin

from agregat.models import Agregat
from agregat.forms import AgregatForm, ChangeAgregatNumForm


class AgregatListView(
    CommonContextMixin,
    ListView,
):
    queryset = Parametr.objects.filter(
        parametr_type__exact=ParamIds.AGREGAT,
    )
    template_name = "agregat/list.html"
    context_object_name = "agregats"


class AgregatDetailView(
    CommonContextMixin,
    DetailView,
):
    template_name = "agregat/detail.html"
    pk_url_kwarg = "agregat_id"
    context_object_name = "agregat"

    def get_object(self):
        agregat_id = self.kwargs.get("agregat_id")
        agregat = Parametr.objects.get(pk=agregat_id)
        return agregat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agregat = self.object
        agregat_parametrs = (
            Agregat.objects.
            filter(agr=agregat)
            .select_related(
                "par"
            )
            .order_by("num")
        )
        context["agr_parametrs"] = agregat_parametrs
        return context


class AgregatParametrCreateView(
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

    def form_valid(self, form):
        instance = form.save(commit=False)
        agregat_id = self.kwargs.get("agregat_id")
        num = Agregat.objects.filter(agr=agregat_id).count() + 1
        setattr(instance, "num", num)
        instance.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agregat_id = self.kwargs.get("agregat_id")
        agregat = Parametr.objects.get(pk=agregat_id)
        context["instance"] = agregat
        return context


class AgregatParametrDeleteView(
    CommonContextMixin,
    DeleteView,
):
    model = Agregat
    template_name = "agregat/agregat.html"
    context_object_name = "instance"

    def get_object(self):
        agregat_id = self.kwargs.get("agregat_id")
        param_id = self.kwargs.get("param_id")
        return (
            Agregat.objects.
            filter(agr=agregat_id, par=param_id)
            .select_related(
                "agr",
                "par"
            )
            .first()
        )

    def get_success_url(self):
        agregat_id = self.kwargs.get("agregat_id")
        return reverse_lazy(
            "agregat:detail",
            kwargs={
                "agregat_id": agregat_id,
            },
        )

    def form_valid(self, form):
        agregat_id = self.kwargs.get("agregat_id")
        instance = self.get_object()
        num = instance.num
        instance.delete()

        for par_agr in Agregat.objects.filter(Q(agr=agregat_id) & Q(num__gt=num)):
            par_agr.num = par_agr.num - 1
            par_agr.save()

        return super().form_valid(form)


class ChangeAgregatNumView(CommonContextMixin, FormView):
    model = Agregat
    template_name = "agregat/change_agr_num.html"
    form_class = ChangeAgregatNumForm

    def get_agregat(self):
        if not hasattr(self, "_agregat"):
            self._agregat = get_object_or_404(
                Parametr, pk=self.kwargs["agregat_id"]
            )
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
