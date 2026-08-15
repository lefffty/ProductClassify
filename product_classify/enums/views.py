from django.urls import reverse_lazy
from django.views.generic import (
    FormView,
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
    CreateView,
)

from core.mixins import CommonContextMixin
from classes.models import ClassStruct

from enums.models import Enums
from enums.forms import EnumsForm, ChangeNumForm


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
        enum_obj: Enums = self.get_object()
        enum_value = enum_obj.value
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
            "enums:list",
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
            "enums:detail",
            kwargs={
                "class_id": class_id,
                "enum_id": pk,
            },
        )


class ChangeEnumsNumView(
    CommonContextMixin,
    FormView
):
    template_name = "enums/change_num.html"
    form_class = ChangeNumForm

    def get_success_url(self):
        return reverse_lazy("classes:index")
