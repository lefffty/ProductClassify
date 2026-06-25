from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin
from django.views.generic import (
    ListView,
    DeleteView,
    DetailView,
    CreateView,
    UpdateView,
)

from product_classify.classes.models import ClassStruct

from .models import Parametr
from .forms import ParametrForm
from .constants import (
    FASTENER_ID,
    AGREGAT_TYPE_ID,
)


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        main_classes = ClassStruct.objects.filter(main_class__exact=FASTENER_ID)
        context["main_classes"] = main_classes
        return context


class ParametrListView(
    CommonContextMixin,
    ListView,
):
    template_name = "parametr/list.html"
    context_object_name = "parameters"
    ordering = "id"

    def get_queryset(self):
        parameters = Parametr.objects.exclude(parametr_type__exact=AGREGAT_TYPE_ID)
        return parameters


class ParametrDetailView(
    CommonContextMixin,
    DetailView,
):
    model = Parametr
    template_name = "parametr/detail.html"
    pk_url_kwarg = "parametr_id"
    context_object_name = "parameter"


class ParametrCreateUpdateDeleteMixin:
    model = Parametr
    template_name = "parametr/parametr.html"


class ParametrCreateView(
    ParametrCreateUpdateDeleteMixin,
    CommonContextMixin,
    CreateView,
):
    form_class = ParametrForm
    success_url = reverse_lazy("parametr:parametr_list")


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
            "parametr:parametr_detail",
            kwargs={
                "parametr_id": pk,
            },
        )


class ParametrDeleteView(
    ParametrCreateUpdateDeleteMixin,
    CommonContextMixin,
    DeleteView,
):
    success_url = reverse_lazy("parametr:parametr_list")
    pk_url_kwarg = "parametr_id"
    context_object_name = "instance"
