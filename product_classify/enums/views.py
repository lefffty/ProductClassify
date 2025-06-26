from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from .models import Enums
from .utils import get_enum_value
from .forms import EnumsForm, ChangeNumForm
from .constants import FASTENER_ID
from classes.models import ClassStruct
from products.models import ParProd


main_classes = ClassStruct.objects.filter(
    main_class__exact=FASTENER_ID
)


def enums_list(
    request: HttpRequest,
    class_id: int,
) -> HttpResponse:
    """
    Список перечислений
    """
    enums = Enums.objects.filter(
        enum__main_class__id=class_id
    ).order_by('id')
    context = {
        'main_classes': main_classes,
        'enums': enums,
    }
    return render(
        request,
        'enums/list.html',
        context,
    )


def enums_detail(
    request: HttpRequest,
    class_id: int,
    enum_id: int,
) -> HttpResponse:
    """
    Страница перечисления
    """
    enum = Enums.objects.get(
        pk=enum_id,
    )
    enum_value = get_enum_value(enum)
    context = {
        'main_classes': main_classes,
        'enum': enum,
        'enum_value': enum_value,
    }
    return render(
        request,
        'enums/detail.html',
        context,
    )


def add_enum(
    request: HttpRequest,
) -> HttpResponse:
    """
    Добавление перечисления
    """
    if request.method == 'POST':
        form = EnumsForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            num_value = Enums.objects.filter(enum__exact=instance.enum).count()
            instance.num = num_value + 1
            instance.save()
            return redirect(
                'classes:index'
            )
    else:
        form = EnumsForm()
    context = {
        'form': form,
        'main_classes': main_classes,
    }
    return render(
        request,
        'enums/enum.html',
        context,
    )


def edit_enum(
    request: HttpRequest,
    class_id: int,
    enum_id: int,
) -> HttpResponse:
    """
    Редактирование перечисления
    """
    instance = Enums.objects.get(pk=enum_id)
    form = EnumsForm(
        request.POST or None,
        instance=instance,
    )
    if form.is_valid():
        form.save(commit=True)
        return redirect(
            'enums:enums_list',
        )
    context = {
        'instance': instance,
        'form': form,
        'main_classes': main_classes,
    }
    return render(
        request,
        'enums/enum.html',
        context,
    )


def delete_enum(
    request: HttpRequest,
    class_id: int,
    enum_id: int,
) -> HttpResponse:
    """
    Удаление перечисления
    """
    instance = Enums.objects.get(pk=enum_id)
    if request.method == 'POST':
        if ParProd.objects.filter(enum_val=instance).exists():
            ParProd.objects.filter(
                enum_val=instance,
            ).delete()
        instance.delete()
        return redirect(
            'enums:enums_list',
            instance.enum.main_class.id,
        )
    context = {
        'instance': instance,
        'main_classes': main_classes,
    }
    return render(
        request,
        'enums/enum.html',
        context,
    )


def change_num(
    request: HttpRequest,
) -> HttpResponse:
    """
    Изменение номера перечисления
    """
    form = ChangeNumForm(request.POST or None)
    if form.is_valid():
        form.clean()
        return redirect(
            'classes:index',
        )
    context = {
        'form': form,
        'main_classes': main_classes,
    }
    return render(
        request,
        'enums/change_num.html',
        context,
    )
