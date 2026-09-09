from django.views.generic import CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy

from core.mixins import CommonContextMixin

from route_tech.forms import (
    EconomicActivitySubjectForm,
    GroupWorkingCenterForm,
    ProdOperationForm,
)
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
