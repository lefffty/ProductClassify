from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.views.generic import (
    ListView,
    DetailView,
)

from .models import Ei
from classes.models import (
    ClassStruct,
)
from .forms import EiForm
from .constants import (
    FASTENER_ID,
)


class EiListView(ListView):
    model = Ei
    template_name = 'ei/list.html'
    ordering = 'id'
    context_object_name = 'eis'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        main_classes = ClassStruct.objects.filter(
            main_class__exact=FASTENER_ID
        )
        fastener_classes = ClassStruct.objects.filter(
            main_class__exact=FASTENER_ID
        )
        context['main_classes'] = main_classes
        context['fastener_classes'] = fastener_classes
        return context


def ei_detail(
    request: HttpRequest,
    ei_id: int,
) -> HttpResponse:
    """
    Страница единицы измерения
    """
    main_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    ei = Ei.objects.get(pk=ei_id)
    context = {
        'ei': ei,
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'ei/detail.html',
        context,
    )


def edit_ei(
    request: HttpRequest,
    ei_id: int,
) -> HttpResponse:
    """
    Редактирование единицы измерения
    """
    main_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    instance = Ei.objects.get(pk=ei_id)
    form = EiForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save(commit=True)
        return redirect('ei:ei_detail', ei_id)
    context = {
        'form': form,
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'ei/ei.html',
        context,
    )


def delete_ei(
    request: HttpRequest,
    ei_id: int,
) -> HttpResponse:
    """
    Удаление единицы измерения
    """
    main_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    instance = Ei.objects.get(pk=ei_id)

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(
                '''SELECT COUNT(*) FROM class_struct
                WHERE base_ei = %s;''',
                [ei_id]
            )
            ref_count = cursor.fetchone()[0]

            if ref_count > 0:
                cursor.execute(
                    '''UPDATE class_struct SET base_ei = NULL
                    WHERE base_ei = %s;''',
                    [ei_id]
                )

        instance.delete()
        return redirect('ei:ei_list')

    context = {
        'instance': instance,
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'ei/ei.html',
        context,
    )


def add_ei(
    request: HttpRequest,
) -> HttpResponse:
    """
    Добавление единицы измерения
    """
    main_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    if request.method == 'POST':
        form = EiForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('ei:ei_list')
    else:
        form = EiForm()
    context = {
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
        'form': form,
    }
    return render(
        request,
        'ei/ei.html',
        context,
    )
