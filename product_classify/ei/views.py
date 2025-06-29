from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
    CreateView,
)

from .models import Ei
from .forms import EiForm
from classes.models import (
    ClassStruct,
)
from .constants import (
    FASTENER_ID,
)


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(
            main_class__exact=FASTENER_ID
        )
        context['fastener_classes'] = fastener_classes
        return context


class EiListView(ListView, CommonContextMixin):
    model = Ei
    template_name = 'ei/list.html'
    ordering = 'id'
    context_object_name = 'eis'


class EiDetailView(DetailView, CommonContextMixin):
    model = Ei
    context_object_name = 'ei'
    template_name = 'ei/detail.html'
    pk_url_kwarg = 'ei_id'


class EiCreateMixin:
    form_class = EiForm
    template_name = 'ei/ei.html'
    model = Ei
    success_url = reverse_lazy('ei:ei_list')


class EiDeleteMixin:
    template_name = 'ei/ei.html'
    model = Ei
    pk_url_kwarg = 'ei_id'
    success_url = reverse_lazy('ei:ei_list')


class EiCreateView(
    EiCreateMixin,
    CreateView,
    CommonContextMixin,
):
    form_class = EiForm
    template_name = 'ei/ei.html'
    model = Ei
    pk_url_kwarg = 'ei_id'
    success_url = reverse_lazy('ei:ei_list')


class EiDeleteView(
    EiDeleteMixin,
    DeleteView,
    CommonContextMixin,
):
    template_name = 'ei/ei.html'
    model = Ei
    pk_url_kwarg = 'ei_id'
    success_url = reverse_lazy('ei:ei_list')


class EiUpdateView(
    UpdateView,
    CommonContextMixin,
):
    form_class = EiForm
    template_name = 'ei/ei.html'
    model = Ei
    pk_url_kwarg = 'ei_id'

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy('ei:ei_detail', kwargs={
            'ei_id': pk,
        })
