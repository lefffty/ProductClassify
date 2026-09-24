from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (
    FormView,
    ListView,
    DetailView,
    DeleteView,
    UpdateView,
    CreateView,
)

from core.mixins import CommonContextMixin, HandbookExecutiveRequiredMixin
from classes.models import ClassStruct

from enums.models import Enums
from enums.forms import EnumsForm, ChangeNumForm


class EnumsListView(
    PermissionRequiredMixin,
    CommonContextMixin,
    ListView,
):
    permission_required = "enums.view_enums"
    template_name = "enums/list.html"
    context_object_name = "enums"

    def get_queryset(self):
        class_id = self.kwargs.get("class_id")
        enums = (
            Enums.objects
            .filter(enum__main_class__id=class_id)
            .select_related("enum", "enum__main_class")
            .order_by("id")
        )
        return enums


class EnumsDetailView(
    PermissionRequiredMixin,
    CommonContextMixin,
    DetailView,
):
    model = Enums
    permission_required = "enums.view_enums"
    template_name = "enums/detail.html"
    context_object_name = "enum"
    pk_url_kwarg = "enum_id"

    def get_queryset(self):
        return (
            Enums.objects
            .select_related(
                "enum",
                "enum__main_class",
            )
        )


class EnumsCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    CreateView,
):
    model = Enums
    form_class = EnumsForm
    template_name = "enums/enum.html"
    success_url = reverse_lazy("classes:index")


class EnumsDeleteView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    DeleteView,
):
    model = Enums
    template_name = "enums/enum.html"
    pk_url_kwarg = "enum_id"
    context_object_name = "instance"

    def get_queryset(self):
        return Enums.objects.select_related(
            "enum__main_class",
        )

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
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    UpdateView,
):
    model = Enums
    form_class = EnumsForm
    template_name = "enums/enum.html"
    pk_url_kwarg = "enum_id"
    context_object_name = "instance"

    def get_queryset(self):
        return Enums.objects.select_related(
            "enum__main_class",
        )

    def get_success_url(self):
        class_id = self.kwargs.get("class_id")
        pk = self.object.pk
        return reverse_lazy(
            "enums:detail",
            kwargs={
                "class_id": class_id,
                "enum_id": pk,
            },
        )


class ChangeEnumsNumView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    FormView,
):
    template_name = "enums/change_num.html"
    form_class = ChangeNumForm

    def get_success_url(self):
        return reverse_lazy("classes:index")
