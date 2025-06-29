from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin
from django.views.generic import (
    ListView,
    DeleteView,
    DetailView,
    CreateView,
    UpdateView,
)

from .models import Parametr
from .forms import ParametrForm
from classes.models import ClassStruct
from .constants import (
    FASTENER_ID,
    AGREGAT_TYPE_ID,
)


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        main_classes = ClassStruct.objects.filter(
           main_class__exact=FASTENER_ID
        )
        context['main_classes'] = main_classes
        return context


class ParametrListView(
    ListView,
    CommonContextMixin,
):
    template_name = 'parametr/list.html'
    context_object_name = 'parameters'
    ordering = 'id'

    def get_queryset(self):
        parameters = Parametr.objects.exclude(
            parametr_type__exact=AGREGAT_TYPE_ID
        )
        return parameters


class ParametrDetailView(
    DetailView,
    CommonContextMixin,
):
    pk_url_kwarg = 'parametr_id'
    model = Parametr
    template_name = 'parametr/detail.html'
    context_object_name = 'parameter'


class ParametrCreateView(
    CreateView,
    CommonContextMixin,
):
    model = Parametr
    template_name = 'parametr/parametr.html'
    success_url = reverse_lazy('parametr:parametr_list')
    form_class = ParametrForm


class ParametrUpdateView(
    UpdateView,
    CommonContextMixin,
):
    model = Parametr
    form_class = ParametrForm
    pk_url_kwarg = 'parametr_id'
    template_name = 'parametr/parametr.html'

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy('parametr:parametr_detail', kwargs={
            'parametr_id': pk,
        })


class ParametrDeleteView(
    DeleteView,
    CommonContextMixin,
):
    model = Parametr
    pk_url_kwarg = 'parametr_id'
    template_name = 'parametr/parametr.html'
    success_url = reverse_lazy('parametr:parametr_list')
    context_object_name = 'instance'
