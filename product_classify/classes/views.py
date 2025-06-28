from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection

from classes.models import (
    ClassStruct,
    ParClass,
)
from classes.forms import (
    ProdClassForm,
    EnumClassForm,
    ParClassForm,
    ChangeParclassNumForm,
)
from .constants import (
    ENUM_CLASSES_IDS,
    FASTENER_ID,
)

main_classes = ClassStruct.objects.filter(
    main_class__exact=FASTENER_ID
)

fastener_classes = ClassStruct.objects.filter(
    main_class__exact=FASTENER_ID
)


def index(
    request: HttpRequest,
) -> HttpResponse:
    """
    Главная страница проекта
    """
    context = {
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'classes/index.html',
        context
    )


def get_category_classes(
    request: HttpRequest,
    class_id: int,
) -> HttpResponse:
    """
    Страница категории классов
    """
    main_class = ClassStruct.objects.get(pk=class_id)
    classes = ClassStruct.objects.filter(
        main_class__exact=class_id
    ).order_by('id')
    context = {
        'main_class': main_class,
        'classes': classes,
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'classes/category.html',
        context,
    )


def add_prod_class(
    request: HttpRequest,
) -> HttpResponse:
    """
    Добавление нового класса изделия
    """
    if request.method == 'POST':
        form = ProdClassForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('classes:index')
    else:
        form = ProdClassForm()
    context = {
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
        'form': form,
    }
    return render(
        request,
        'classes/prod_class.html',
        context
    )


def add_enum_class(
    request: HttpRequest,
) -> HttpResponse:
    """
    Добавление нового класса перечисления
    """
    if request.method == 'POST':
        form = EnumClassForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('classes:index')
    else:
        form = EnumClassForm()
    context = {
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
        'form': form,
    }
    return render(
        request,
        'classes/enum_class.html',
        context
    )


def edit_class(
    request: HttpRequest,
    class_id: int,
) -> HttpResponse:
    """
    Редактирование класса
    """
    _class = ClassStruct.objects.get(pk=class_id)
    context = {
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    if _class.id in ENUM_CLASSES_IDS:
        context = {
            'main_classes': main_classes,
            'fastener_classes': fastener_classes,
        }
        form = EnumClassForm(
            request.POST or None,
            instance=_class,
        )
        if form.is_valid():
            form.save(commit=True)
            return redirect(
                'classes:category_classes',
                _class.main_class.id,
            )
        context['form'] = form
        return render(
            request,
            'classes/enum_class.html',
            context,
        )
    else:
        form = ProdClassForm(
            request.POST or None,
            instance=_class,
        )
        if form.is_valid():
            form.save(commit=True)
            return redirect(
                'classes:category_classes',
                _class.main_class.id,
            )
        context['form'] = form
        return render(
            request,
            'classes/prod_class.html',
            context,
        )


def delete_class(
    request: HttpRequest,
    class_id: int,
) -> HttpResponse:
    """
    Удаление класса
    """
    _class = ClassStruct.objects.get(pk=class_id)
    main_class_id = _class.main_class.id
    context = {
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
        'instance': _class,
    }
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(
                f'''SELECT * FROM delete_class_and_descendants(
                    {_class.id}
                );'''
            )
            data = cursor.fetchone()[0]
            if data:
                return redirect(
                    'classes:category_classes',
                    main_class_id
                )
    return render(
        request,
        'classes/enum_class.html',
        context,
    )


def class_params_list(
    request: HttpRequest,
    class_id: int,
) -> HttpResponse:
    """
    Страница параметров класса
    """
    _class = ClassStruct.objects.get(
        pk=class_id,
    )
    params = ParClass.objects.filter(
        class_field=class_id,
    ).order_by('num')
    context = {
        'class': _class,
        'params': params,
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'classes/params.html',
        context,
    )


def add_param_class(
    request: HttpRequest,
    class_id: int,
) -> HttpResponse:
    """
    Добавление параметра класса
    """
    _class = ClassStruct.objects.get(pk=class_id,)
    if request.method == 'POST':
        form = ParClassForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect(
                'classes:class_params_list',
                class_id,
            )
    else:
        form = ParClassForm(class_field=_class)
    context = {
        'instance': _class,
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
        'form': form,
    }
    return render(
        request,
        'classes/param_class.html',
        context,
    )


def edit_param_class(
    request: HttpRequest,
    class_id: int,
    param_id: int,
) -> HttpResponse:
    """
    Редактирование параметра класса
    """
    instance = ParClass.objects.get(
        class_field=class_id,
        parametr=param_id,
    )
    form = ParClassForm(
        request.POST or None,
        instance=instance,
    )
    if form.is_valid():
        form.save(commit=True)
        return redirect(
            'classes:class_params_list',
            class_id
        )
    context = {
        'instance': instance,
        'main_classes': main_classes,
        'form': form,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'classes/param_class.html',
        context,
    )


def delete_param_class(
    request: HttpRequest,
    class_id: int,
    param_id: int,
) -> HttpResponse:
    """
    Удаление параметра класса
    """
    instance = ParClass.objects.get(
        class_field=class_id,
        parametr=param_id,
    )
    if request.method == 'POST':
        instance.delete()
        return redirect(
            'classes:class_params_list',
            class_id
        )
    context = {
        'instance': instance,
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'classes/param_class.html',
        context,
    )


def change_parclass_num(
    request: HttpRequest,
    class_id: int,
) -> HttpResponse:
    """
    Изменение номера параметра класса
    """
    _class = ClassStruct.objects.get(pk=class_id)
    if request.method == 'POST':
        form = ChangeParclassNumForm(request.POST, class_id=class_id)
        if form.is_valid():
            instance_1 = form.cleaned_data['class_field_1']
            instance_2 = form.cleaned_data['class_field_2']
            instance_1.num = instance_2.num
            instance_2.num = instance_1.num
            instance_1.save()
            instance_2.save()
            return redirect(
                'classes:class_params_list',
                class_id,
            )
    else:
        form = ChangeParclassNumForm(class_id=class_id)
    context = {
        'main_classes': main_classes,
        'fastener_classes': fastener_classes,
        'instance': _class,
        'form': form,
    }
    return render(
        request,
        'classes/change_parclass_num.html',
        context,
    )
