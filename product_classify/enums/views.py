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

from classes.models import ClassStruct

from .models import Enums
from .utils import get_enum_value
from .forms import EnumsForm, ChangeNumForm
from .constants import FASTENER_ID


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(main_class__exact=FASTENER_ID)
        context["fastener_classes"] = fastener_classes
        return context


class EnumsListView(
    CommonContextMixin,
    ListView,
):
    template_name = "enums/list.html"
    context_object_name = "enums"

    def get_queryset(self):
        class_id = self.kwargs.get("class_id")
        enums = Enums.objects.filter(enum__main_class__id=class_id).order_by("id")
        return enums


class EnumsDetailView(
    CommonContextMixin,
    DetailView,
):
    model = Enums
    template_name = "enums/detail.html"
    context_object_name = "enum"
    pk_url_kwarg = "enum_id"

    def get_context_data(self, **kwargs):
        enum_value = get_enum_value(self.get_object())
        context = super().get_context_data(**kwargs)
        context["enum_value"] = enum_value
        return context


class EnumsCreateView(
    CommonContextMixin,
    CreateView,
):
    model = Enums
    form_class = EnumsForm
    template_name = "enums/enum.html"
    success_url = reverse_lazy("classes:index")


class EnumsDeleteView(
    CommonContextMixin,
    DeleteView,
):
    model = Enums
    template_name = "enums/enum.html"
    pk_url_kwarg = "enum_id"
    context_object_name = "instance"

    def get_success_url(self):
        class_id = self.kwargs.get("class_id")
        enum_pk = ClassStruct.objects.get(pk=class_id).main_class.pk
        return reverse_lazy(
            "enums:enums_list",
            kwargs={
                "class_id": enum_pk,
            },
        )


class EnumsUpdateView(
    CommonContextMixin,
    UpdateView,
):
    model = Enums
    form_class = EnumsForm
    template_name = "enums/enum.html"
    pk_url_kwarg = "enum_id"
    context_object_name = "instance"

    def get_success_url(self):
        class_id = self.kwargs.get("class_id")
        pk = self.get_object().pk
        return reverse_lazy(
            "enums:enums_detail",
            kwargs={
                "class_id": class_id,
                "enum_id": pk,
            },
        )


def change_num(
    request: HttpRequest,
) -> HttpResponse:
    """
    Изменение номера перечисления
    """
    fastener_classes = ClassStruct.objects.filter(main_class__exact=FASTENER_ID)
    form = ChangeNumForm(request.POST or None)
    if form.is_valid():
        form.clean()
        return redirect(
            "classes:index",
        )
    context = {
        "form": form,
        "fastener_classes": fastener_classes,
    }
    return render(
        request,
        "enums/change_num.html",
        context,
    )
