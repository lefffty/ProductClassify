from django.shortcuts import render, redirect
from django.http import (
    HttpRequest,
    HttpResponse,
)

from .models import Parametr
from .forms import ParametrForm
from classes.models import ClassStruct
from .constants import (
    FASTENER_ID,
    AGREGAT_TYPE_ID,
)


main_classes = ClassStruct.objects.filter(
    main_class__exact=FASTENER_ID
)


def parametr_list(
    request: HttpRequest,
) -> HttpResponse:
    """
    Список параметров
    """
    parameters = Parametr.objects.exclude(
        parametr_type__exact=AGREGAT_TYPE_ID
    )
    context = {
        'main_classes': main_classes,
        'parameters': parameters
    }
    return render(
        request,
        'parametr/list.html',
        context,
    )


def parametr_detail(
    request: HttpRequest,
    parametr_id: int,
) -> HttpResponse:
    """
    Страница параметра
    """
    parameter = Parametr.objects.get(pk=parametr_id)
    context = {
        'parameter': parameter,
        'main_classes': main_classes,
    }
    return render(
        request,
        'parametr/detail.html',
        context,
    )


def add_parametr(
    request: HttpRequest,
) -> HttpResponse:
    """
    Добавление параметра
    """
    if request.method == 'POST':
        form = ParametrForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('parametr:parametr_list')
    else:
        form = ParametrForm()
    context = {
        'form': form,
        'main_classes': main_classes,
    }
    return render(
        request,
        'parametr/parametr.html',
        context,
    )


def edit_parametr(
    request: HttpRequest,
    parametr_id: int,
) -> HttpResponse:
    """
    Редактирование параметра
    """
    instance = Parametr.objects.get(pk=parametr_id)
    form = ParametrForm(
        request.POST or None,
        instance=instance,
    )
    if form.is_valid():
        form.save(commit=True)
        return redirect('parametr:parametr_detail', id=parametr_id,)
    context = {
        'main_classes': main_classes,
        'form': form,
    }
    return render(
        request,
        'parametr/parametr.html',
        context,
    )


def delete_parametr(
    request: HttpRequest,
    parametr_id: int,
) -> HttpResponse:
    """
    Удаление параметра
    """
    instance = Parametr.objects.get(pk=parametr_id)
    if request.method == 'POST':
        instance.delete()
        return redirect('parametr:parametr_list')
    context = {
        'instance': instance,
        'main_classes': main_classes,
    }
    return render(
        request,
        'parametr/parametr.html',
        context,
    )
