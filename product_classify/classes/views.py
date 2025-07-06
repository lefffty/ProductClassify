from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.db import connection
from django.views.generic.base import ContextMixin
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
    CreateView,
    TemplateView,
)

from classes.models import (
    ClassStruct,
    ParClass,
)
from classes.forms import (
    ChangeParclassNumForm,
    ProdClassForm,
    EnumClassForm,
    ParClassForm,
)
from .constants import (
    ENUM_CLASSES_IDS,
    FASTENER_ID,
)

fastener_classes = ClassStruct.objects.filter(
    main_class__exact=FASTENER_ID
)


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(
            main_class__exact=FASTENER_ID
        )
        context['fastener_classes'] = fastener_classes
        return context


class MainPageTemplateView(
    CommonContextMixin,
    TemplateView,
):
    template_name = 'classes/index.html'


class CategoryClassesListView(
    CommonContextMixin,
    ListView,
):
    template_name = 'classes/category.html'
    model = ClassStruct
    context_object_name = 'classes'

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        classes = ClassStruct.objects.filter(
            main_class__exact=class_id
        ).order_by('id')
        return classes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        main_class = ClassStruct.objects.get(pk=class_id)
        context['main_class'] = main_class
        return context


class ProdClassCreateView(
    CommonContextMixin,
    CreateView,
):
    form_class = ProdClassForm
    success_url = reverse_lazy('classes:index')
    template_name = 'classes/prod_class.html'


class EnumClassCreateView(
    CommonContextMixin,
    CreateView,
):
    form_class = EnumClassForm
    success_url = reverse_lazy('classes:index')
    template_name = 'classes/enum_class.html'


class ClassUpdateView(
    CommonContextMixin,
    UpdateView,
):
    def get_object(self):
        class_id = self.kwargs.get('class_id')
        _class = ClassStruct.objects.get(pk=class_id)
        return _class

    def get_template_names(self):
        class_id = self.kwargs.get('class_id')
        _class = ClassStruct.objects.get(pk=class_id)
        if _class.pk in ENUM_CLASSES_IDS:
            return ['classes/enum_class.html']
        return ['classes/prod_class.html']

    def get_form_class(self):
        class_id = self.kwargs.get('class_id')
        _class = ClassStruct.objects.get(pk=class_id)
        if _class.pk in ENUM_CLASSES_IDS:
            return EnumClassForm
        return ProdClassForm

    def get_success_url(self):
        class_id = self.kwargs.get('class_id')
        _class = ClassStruct.objects.get(pk=class_id)
        return reverse_lazy(
            'classes:category_classes',
            kwargs={
                'class_id': _class.main_class.pk,
            }
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


class ClassParamsListView(
    CommonContextMixin,
    ListView,
):
    template_name = 'classes/params.html'
    context_object_name = 'params'

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        params = ParClass.objects.filter(
            class_field=class_id,
        ).order_by('num')
        return params

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        _class = ClassStruct.objects.get(
            pk=class_id,
        )
        context['class'] = _class
        return context


class ClassParamCreateView(
    CommonContextMixin,
    CreateView,
):
    template_name = 'classes/param_class.html'
    form_class = ParClassForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _class = ClassStruct.objects.get(pk=self.kwargs.get('class_id'))
        context['instance'] = _class
        return context

    def get_success_url(self):
        return reverse_lazy(
            'classes:class_params_list',
            kwargs={
                'class_id': self.kwargs.get('class_id')
            }
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
        'fastener_classes': fastener_classes,
        'instance': _class,
        'form': form,
    }
    return render(
        request,
        'classes/change_parclass_num.html',
        context,
    )


class ChangeNumView(
    CommonContextMixin,
    UpdateView,
):
    queryset = ParClass.objects.all()
    form_class = ChangeParclassNumForm
    template_name = 'classes/change_parclass_num.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        _class = ClassStruct.objects.get(pk=class_id)
        context['instance'] = _class
        return context

    def form_valid(self, form):
        instance_1 = form.cleaned_data['class_field_1']
        instance_2 = form.cleaned_data['class_field_2']
        instance_1.num = instance_2.num
        instance_2.num = instance_1.num
        instance_1.save()
        instance_2.save()

    def get_success_url(self):
        class_id = self.kwargs.get('class_id')
        return reverse_lazy(
            'classes:class_params_list',
            kwargs={
                'class_id': class_id,
            }
        )
