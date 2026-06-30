from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
)

from parametr.models import Parametr
from classes.models import ClassStruct
from core.mixins import CommonContextMixin

from .models import Agregat
from .forms import AgregatForm, ChangeAgregatNumForm
from .constants import (
    FASTENER_ID,
    AGREGAT_TYPE_ID,
)


class AgregatListView(
    CommonContextMixin,
    ListView,
):
    queryset = Parametr.objects.filter(
        parametr_type__exact=AGREGAT_TYPE_ID,
    )
    template_name = "agregat/list.html"
    context_object_name = "agregats"


class AgregatDetailView(
    CommonContextMixin,
    DetailView,
):
    template_name = "agregat/detail.html"
    pk_url_kwarg = "agregat_id"

    def get_object(self):
        agregat_id = self.kwargs.get("agregat_id")
        agregat = Parametr.objects.get(pk=agregat_id)
        return agregat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agregat_parametrs = Agregat.objects.filter(agr=self.get_object()).order_by(
            "num"
        )
        context["agr_parametrs"] = agregat_parametrs
        context["agregat"] = self.get_object()
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
            "agregat:agregat_detail",
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
        return Agregat.objects.get(agr=agregat_id, par=param_id)

    def get_success_url(self):
        agregat_id = self.kwargs.get("agregat_id")
        return reverse_lazy(
            "agregat:agregat_detail",
            kwargs={
                "agregat_id": agregat_id,
            },
        )

    def form_valid(self, form):
        agregat_id = self.kwargs.get("agregat_id")
        instance = self.get_object()
        instance.delete()

        for par_agr in Agregat.objects.filter(agr=agregat_id):
            if par_agr.num > instance.num:
                par_agr.num = par_agr.num - 1
                par_agr.save()
        return super().form_valid(form)


def change_agregat_num(
    request: HttpRequest,
    agregat_id: int,
) -> HttpResponse:
    """
    Изменение номера параметра в агрегат
    """
    fastener_classes = ClassStruct.objects.filter(main_class__exact=FASTENER_ID)
    agregat = Parametr.objects.get(pk=agregat_id)
    form = ChangeAgregatNumForm(request.POST or None, agr=agregat)
    if form.is_valid():
        return redirect(
            "agregat:agregat_detail",
            agregat_id,
        )
    context = {
        "instance": agregat,
        "form": form,
        "fastener_classes": fastener_classes,
    }
    return render(
        request,
        "agregat/change_agr_num.html",
        context,
    )
