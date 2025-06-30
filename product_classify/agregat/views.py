from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
    CreateView,
)

from parametr.models import Parametr
from .models import Agregat
from .forms import AgregatForm, ChangeAgregatNumForm
from classes.models import ClassStruct
from .constants import (
    FASTENER_ID,
    AGREGAT_TYPE_ID,
)


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(
            main_class__exact=FASTENER_ID
        )
        context['fastener_classes'] = fastener_classes
        return context


class AgregatListView(
    CommonContextMixin,
    ListView,
):
    queryset = Parametr.objects.filter(
        parametr_type__exact=AGREGAT_TYPE_ID,
    )
    template_name = 'agregat/list.html'
    context_object_name = 'agregats'


class AgregatDetailView(
    CommonContextMixin,
    DetailView,
):
    template_name = 'agregat/detail.html'
    pk_url_kwarg = 'agregat_id'

    def get_object(self):
        agregat_id = self.kwargs.get('agregat_id')
        agregat = Parametr.objects.get(pk=agregat_id)
        return agregat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agregat_parametrs = Agregat.objects.filter(agr=self.get_object())
        context['agr_parametrs'] = agregat_parametrs
        context['agregat'] = self.get_object()
        return context


fastener_classes = ClassStruct.objects.filter(
    main_class__exact=FASTENER_ID
)


def add_parametr_to_agregat(
    request: HttpRequest,
    agregat_id: int,
) -> HttpResponse:
    """
    Добавление параметра в агрегат
    """
    agregat = Parametr.objects.get(pk=agregat_id)
    if request.method == 'POST':
        form = AgregatForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            counter = Agregat.objects.filter(agr=agregat_id).count() + 1
            instance.agr = Parametr.objects.get(id=agregat_id)
            instance.num = counter
            instance.save()
            return redirect(
                'agregat:agregat_detail',
                agregat_id,
            )
    else:
        form = AgregatForm(agr=agregat)
    context = {
        'instance': agregat,
        'form': form,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'agregat/agregat.html',
        context,
    )


def delete_parametr_from_agregat(
    request: HttpRequest,
    agregat_id: int,
    param_id: int,
) -> HttpResponse:
    """
    Удаление параметра из агрегата
    """
    instance = Agregat.objects.get(agr=agregat_id, par=param_id)
    if request.method == 'POST':
        instance.delete()

        for par_agr in Agregat.objects.filter(agr=agregat_id):
            if par_agr.num > instance.num:
                par_agr.num = par_agr.num - 1
                par_agr.save()

        return redirect(
            'agregat:agregat_detail',
            agregat_id,
        )
    context = {
        'instance': instance,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'agregat/agregat.html',
        context,
    )


def change_agregat_num(
    request: HttpRequest,
    agregat_id: int,
) -> HttpResponse:
    """
    Изменение номера параметра в агрегат
    """
    agregat = Parametr.objects.get(pk=agregat_id)
    if request.method == 'POST':
        form = ChangeAgregatNumForm(request.POST, agr=agregat)
        if form.is_valid():
            agr_param_1 = form.cleaned_data['agr_param_1']
            agr_param_2 = form.cleaned_data['agr_param_2']
            agr_param_1.num = agr_param_2.num
            agr_param_2.num = agr_param_1.num
            agr_param_1.save()
            agr_param_2.save()
        return redirect(
            'agregat:agregat_detail',
            agregat_id,
        )
    else:
        form = ChangeAgregatNumForm(agr=agregat)
    context = {
        'instance': agregat,
        'form': form,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'agregat/change_agr_num.html',
        context,
    )
