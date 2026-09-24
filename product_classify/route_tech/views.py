from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404

from loguru import logger

from core.mixins import CommonContextMixin

from core.views import get_context_data
from products.models import Prod

from route_tech.forms import (
    EconomicActivitySubjectForm,
    ProdOperationPosFormSet,
    GroupWorkingCenterForm,
    ProdOperationForm,
)
from route_tech.constants import FormSetConsts
from route_tech.models import EconomicActivitySubject, GroupWorkingCenter, ProdOperation


class EASCreateView(CommonContextMixin, CreateView):
    template_name = "route_tech/eas/eas.html"
    model = EconomicActivitySubject
    form_class = EconomicActivitySubjectForm
    success_url = reverse_lazy("classes:index")


class EASUpdateView(CommonContextMixin, UpdateView):
    model = EconomicActivitySubject
    template_name = "route_tech/eas/eas.html"
    form_class = EconomicActivitySubjectForm
    pk_url_kwarg = "eas_id"

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy(
            "route_tech:detail_eas",
            kwargs={
                "eas_id": pk,
            },
        )


class EASDetailView(CommonContextMixin, DetailView):
    model = EconomicActivitySubject
    pk_url_kwarg = "eas_id"
    template_name = "route_tech/eas/detail.html"
    context_object_name = "subject"


class EASDeleteView(CommonContextMixin, DeleteView):
    model = EconomicActivitySubject
    pk_url_kwarg = "eas_id"
    template_name = "route_tech/eas/eas.html"
    success_url = reverse_lazy("classes:index")
    context_object_name = "subject"


class GWCCreateView(CommonContextMixin, CreateView):
    template_name = "route_tech/gwc/gwc.html"
    model = GroupWorkingCenter
    form_class = GroupWorkingCenterForm
    success_url = reverse_lazy("classes:index")


class GWCUpdateView(CommonContextMixin, UpdateView):
    model = GroupWorkingCenter
    pk_url_kwarg = "gwc_id"
    form_class = GroupWorkingCenterForm
    template_name = "route_tech/gwc/gwc.html"

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy("route_tech:detail_gwc", kwargs={"gwc_id": pk})


class GWCDetailView(CommonContextMixin, DetailView):
    template_name = "route_tech/gwc/detail.html"
    model = GroupWorkingCenter
    pk_url_kwarg = "gwc_id"


class GWCDeleteView(CommonContextMixin, DeleteView):
    model = GroupWorkingCenter
    pk_url_kwarg = "gwc_id"
    template_name = "route_tech/gwc/gwc.html"
    success_url = reverse_lazy("classes:index")
    context_object_name = "center"


class ProdOperationCreateView(CommonContextMixin, CreateView):
    template_name = "route_tech/prod_operation/prod_operation.html"
    model = ProdOperation
    form_class = ProdOperationForm
    success_url = reverse_lazy("classes:index")


class ProdOperationDeleteView(CommonContextMixin, DeleteView):
    template_name = "route_tech/prod_operation/prod_operation.html"
    model = ProdOperation
    context_object_name = "instance"
    pk_url_kwarg = "prod_oper_id"
    success_url = reverse_lazy("classes:index")


class ProdOperationUpdateView(CommonContextMixin, UpdateView):
    template_name = "route_tech/prod_operation/prod_operation.html"
    model = ProdOperation
    pk_url_kwarg = "prod_oper_id"
    form_class = ProdOperationForm

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy(
            "route_tech:detail_prod_operation",
            kwargs={
                "prod_oper_id": pk,
            },
        )


class ProdOperationDetailView(CommonContextMixin, DetailView):
    model = ProdOperation
    pk_url_kwarg = "prod_oper_id"
    template_name = "route_tech/prod_operation/prod_operation.html"


def edit_prod_operation_positions_view(request: HttpRequest, product_id: int):
    context = get_context_data()
    product = Prod.objects.get(pk=product_id)
    edit_mode = request.GET.get("edit") == "1"
    prod_operation = get_object_or_404(ProdOperation, prod=product)

    if request.method == "POST":
        edit_mode = True
        formset = ProdOperationPosFormSet(request.POST, instance=prod_operation)
        if formset.is_valid():
            formset.save()
            return redirect("products:detail", product_id=product_id)
        else:
            logger.info(formset.errors)
    else:
        formset = ProdOperationPosFormSet(instance=prod_operation)
        if not edit_mode:
            for form in formset:
                for field in form.fields.values():
                    field.disabled = True
            formset.extra = FormSetConsts.EXTRA
            formset.can_delete = False

    context.update({
        "formset": formset,
        "product": product,
        "parent_prod_oper": product,
        "prod_operation": prod_operation,
        "edit_mode": edit_mode,
    })

    return render(
        request,
        "products/prodoperation_pos_edit.html",
        context=context,
    )
