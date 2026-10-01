from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required
from django.http import HttpRequest
from django.contrib.auth.mixins import PermissionRequiredMixin
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
from route_tech.selectors import EASSelector
from route_tech.constants import FormSetConsts
from route_tech.models import EconomicActivitySubject, GroupWorkingCenter, ProdOperation


class EASListView(PermissionRequiredMixin, CommonContextMixin, ListView):
    permission_required = "route_tech.view_economicactivitysubject"
    template_name = "route_tech/eas/list.html"
    ordering = "id"
    model = EconomicActivitySubject
    context_object_name = "subjects"


class EASCreateView(PermissionRequiredMixin, CommonContextMixin, CreateView):
    permission_required = "route_tech.add_economicactivitysubject"
    template_name = "route_tech/eas/eas.html"
    model = EconomicActivitySubject
    form_class = EconomicActivitySubjectForm
    success_url = reverse_lazy("classes:index")


class EASUpdateView(PermissionRequiredMixin, CommonContextMixin, UpdateView):
    permission_required = "route_tech.add_economicactivitysubject"
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


class EASDetailView(PermissionRequiredMixin, CommonContextMixin, DetailView):
    permission_required = "route_tech.view_economicactivitysubject"
    model = EconomicActivitySubject
    pk_url_kwarg = "eas_id"
    template_name = "route_tech/eas/detail.html"
    context_object_name = "subject"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eas_id = self.kwargs.get("eas_id")
        children = EASSelector.get_all_eas_descendants(eas_id)
        context["children"] = children
        return context


class EASDeleteView(PermissionRequiredMixin, CommonContextMixin, DeleteView):
    permission_required = "route_tech.delete_economicactivitysubject"
    model = EconomicActivitySubject
    pk_url_kwarg = "eas_id"
    template_name = "route_tech/eas/eas.html"
    success_url = reverse_lazy("classes:index")
    context_object_name = "subject"


class GWCListView(PermissionRequiredMixin, CommonContextMixin, ListView):
    permission_required = "route_tech.view_groupworkingcenter"
    model = GroupWorkingCenter
    template_name = "route_tech/gwc/list.html"
    context_object_name = "centers"


class GWCCreateView(PermissionRequiredMixin, CommonContextMixin, CreateView):
    permission_required = "route_tech.add_groupworkingcenter"
    template_name = "route_tech/gwc/gwc.html"
    model = GroupWorkingCenter
    form_class = GroupWorkingCenterForm
    success_url = reverse_lazy("classes:index")


class GWCUpdateView(PermissionRequiredMixin, CommonContextMixin, UpdateView):
    permission_required = "route_tech.change_groupworkingcenter"
    model = GroupWorkingCenter
    pk_url_kwarg = "gwc_id"
    form_class = GroupWorkingCenterForm
    template_name = "route_tech/gwc/gwc.html"

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy("route_tech:detail_gwc", kwargs={"gwc_id": pk})


class GWCDetailView(PermissionRequiredMixin, CommonContextMixin, DetailView):
    permission_required = "route_tech.view_groupworkingcenter"
    template_name = "route_tech/gwc/detail.html"
    context_object_name = "center"
    model = GroupWorkingCenter
    pk_url_kwarg = "gwc_id"


class GWCDeleteView(PermissionRequiredMixin, CommonContextMixin, DeleteView):
    permission_required = "route_tech.delete_groupworkingcenter"
    model = GroupWorkingCenter
    pk_url_kwarg = "gwc_id"
    template_name = "route_tech/gwc/gwc.html"
    success_url = reverse_lazy("classes:index")
    context_object_name = "center"


class ProdOperationListView(PermissionRequiredMixin, CommonContextMixin, ListView):
    permission_required = "route_tech.view_prodoperation"
    template_name = "route_tech/prod_operation/list.html"
    model = ProdOperation
    context_object_name = "operations"


class ProdOperationCreateView(PermissionRequiredMixin, CommonContextMixin, CreateView):
    permission_required = "route_tech.add_prodoperation"
    template_name = "route_tech/prod_operation/prod_operation.html"
    model = ProdOperation
    form_class = ProdOperationForm
    success_url = reverse_lazy("classes:index")


class ProdOperationDeleteView(PermissionRequiredMixin, CommonContextMixin, DeleteView):
    permission_required = "route_tech.delete_prodoperation"
    template_name = "route_tech/prod_operation/prod_operation.html"
    model = ProdOperation
    context_object_name = "instance"
    pk_url_kwarg = "prod_oper_id"
    success_url = reverse_lazy("classes:index")


class ProdOperationUpdateView(PermissionRequiredMixin, CommonContextMixin, UpdateView):
    permission_required = "route_tech.change_prodoperation"
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


class ProdOperationDetailView(PermissionRequiredMixin, CommonContextMixin, DetailView):
    permission_required = "route_tech.view_prodoperation"
    model = ProdOperation
    context_object_name = "instance"
    pk_url_kwarg = "prod_oper_id"
    template_name = "route_tech/prod_operation/detail.html"


@permission_required("route_tech.change_prodoperationpos")
def edit_prod_operation_positions_view(request: HttpRequest, product_id: int):
    context = get_context_data()
    product = get_object_or_404(Prod, pk=product_id)
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
