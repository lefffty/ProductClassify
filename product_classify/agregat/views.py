from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from parametr.models import Parametr
from .models import Agregat
from .forms import AgregatForm, ChangeAgregatNumForm
from classes.models import ClassStruct
from .constants import (
    FASTENER_ID,
    AGREGAT_TYPE_ID,
)


main_classes = ClassStruct.objects.filter(
    main_class__exact=FASTENER_ID
)

fastener_classes = ClassStruct.objects.filter(
    main_class__exact=FASTENER_ID
)


def agregat_list(
    request: HttpRequest,
) -> HttpResponse:
    """
    Список агрегатов
    """
    agregats = Parametr.objects.filter(
        parametr_type__exact=AGREGAT_TYPE_ID,
    )
    context = {
        'main_classes': main_classes,
        'agregats': agregats,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'agregat/list.html',
        context,
    )


def agregat_detail(
    request: HttpRequest,
    agregat_id: int,
) -> HttpResponse:
    """
    Страница агрегата
    """
    agregat = Parametr.objects.get(pk=agregat_id)
    agr_parametrs = Agregat.objects.filter(agr=agregat.id).order_by('num')
    context = {
        'agregat': agregat,
        'main_classes': main_classes,
        'agr_parametrs': agr_parametrs,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'agregat/detail.html',
        context,
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
        'main_classes': main_classes,
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
        'main_classes': main_classes,
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
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'agregat/change_agr_num.html',
        context,
    )
