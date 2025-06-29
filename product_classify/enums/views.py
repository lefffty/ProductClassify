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

from .models import Enums
from .utils import get_enum_value
from .forms import EnumsForm, ChangeNumForm
from .constants import FASTENER_ID
from classes.models import ClassStruct
from products.models import ParProd


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(
            main_class__exact=FASTENER_ID
        )
        context['fastener_classes'] = fastener_classes
        return context


class EnumsListView(
    ListView,
    CommonContextMixin,
):
    template_name = 'enums/list.html'
    context_object_name = 'enums'

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        enums = Enums.objects.filter(
            enum__main_class__id=class_id
        ).order_by('id')
        return enums


class EnumsDetailView(
    DetailView,
    CommonContextMixin,
):
    model = Enums
    template_name = 'enums/detail.html'
    context_object_name = 'enum'
    pk_url_kwarg = 'enum_id'

    def get_context_data(self, **kwargs):
        enum_value = get_enum_value(self.get_object())
        context = super().get_context_data(**kwargs)
        context['enum_value'] = enum_value
        return context


class EnumsCreateView(
    CreateView,
    CommonContextMixin,
):
    model = Enums
    form_class = EnumsForm
    template_name = 'enums/enum.html'

    def get_success_url(self):
        print(self.get_object())
        return super().get_success_url()


class EnumsDeleteView(
    DeleteView,
    CommonContextMixin,
):
    model = Enums
    template_name = 'enums/enum.html'
    pk_url_kwarg = 'enum_id'
    context_object_name = 'instance'

    def get_success_url(self):
        class_id = self.kwargs.get('class_id')
        enum_pk = ClassStruct.objects.get(pk=class_id).main_class.pk
        return reverse_lazy(
            'enums:enums_list',
            kwargs={
                'class_id': enum_pk,
            }
        )


class EnumsUpdateView(
    UpdateView,
    CommonContextMixin,
):
    model = Enums
    form_class = EnumsForm
    template_name = 'enums/enum.html'
    pk_url_kwarg = 'enum_id'
    context_object_name = 'instance'

    def get_success_url(self):
        class_id = self.kwargs.get('class_id')
        pk = self.get_object().pk
        return reverse_lazy(
            'enums:enums_detail',
            kwargs={
                'class_id': class_id,
                'enum_id': pk,
            }
        )


# def enums_list(
#     request: HttpRequest,
#     class_id: int,
# ) -> HttpResponse:
#     """
#     Список перечислений
#     """
#     enums = Enums.objects.filter(
#         enum__main_class__id=class_id
#     ).order_by('id')
#     context = {
#         'main_classes': main_classes,
#         'enums': enums,
#     }
#     return render(
#         request,
#         'enums/list.html',
#         context,
#     )


# def enums_detail(
#     request: HttpRequest,
#     class_id: int,
#     enum_id: int,
# ) -> HttpResponse:
#     """
#     Страница перечисления
#     """
#     enum = Enums.objects.get(
#         pk=enum_id,
#     )
#     enum_value = get_enum_value(enum)
#     context = {
#         'main_classes': main_classes,
#         'enum': enum,
#         'enum_value': enum_value,
#     }
#     return render(
#         request,
#         'enums/detail.html',
#         context,
#     )


# def add_enum(
#     request: HttpRequest,
# ) -> HttpResponse:
#     """
#     Добавление перечисления
#     """
#     if request.method == 'POST':
#         form = EnumsForm(request.POST)
#         if form.is_valid():
#             instance = form.save(commit=False)
#             num_value = Enums.objects.filter(enum__exact=instance.enum).count()
#             instance.num = num_value + 1
#             instance.save()
#             return redirect(
#                 'classes:index'
#             )
#     else:
#         form = EnumsForm()
#     context = {
#         'form': form,
#         'main_classes': main_classes,
#     }
#     return render(
#         request,
#         'enums/enum.html',
#         context,
#     )


# def edit_enum(
#     request: HttpRequest,
#     class_id: int,
#     enum_id: int,
# ) -> HttpResponse:
#     """
#     Редактирование перечисления
#     """
#     instance = Enums.objects.get(pk=enum_id)
#     form = EnumsForm(
#         request.POST or None,
#         instance=instance,
#     )
#     if form.is_valid():
#         form.save(commit=True)
#         return redirect(
#             'enums:enums_list',
#         )
#     context = {
#         'instance': instance,
#         'form': form,
#         'main_classes': main_classes,
#     }
#     return render(
#         request,
#         'enums/enum.html',
#         context,
#     )


# def delete_enum(
#     request: HttpRequest,
#     class_id: int,
#     enum_id: int,
# ) -> HttpResponse:
#     """
#     Удаление перечисления
#     """
#     instance = Enums.objects.get(pk=enum_id)
#     if request.method == 'POST':
#         if ParProd.objects.filter(enum_val=instance).exists():
#             ParProd.objects.filter(
#                 enum_val=instance,
#             ).delete()
#         instance.delete()
#         return redirect(
#             'enums:enums_list',
#             instance.enum.main_class.id,
#         )
#     context = {
#         'instance': instance,
#         'main_classes': main_classes,
#     }
#     return render(
#         request,
#         'enums/enum.html',
#         context,
#     )


def change_num(
    request: HttpRequest,
) -> HttpResponse:
    """
    Изменение номера перечисления
    """
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    form = ChangeNumForm(request.POST or None)
    if form.is_valid():
        form.clean()
        return redirect(
            'classes:index',
        )
    context = {
        'form': form,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'enums/change_num.html',
        context,
    )
