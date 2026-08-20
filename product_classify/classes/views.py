from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import (
    FormView,
    ListView,
    UpdateView,
    CreateView,
    DeleteView,
    TemplateView,
)

from core.mixins import CommonContextMixin

from classes.models import (
    ClassStruct,
    ParClass,
)
from classes.forms import (
    ChangeParClassNumForm,
    ProdClassForm,
    EnumClassForm,
    ParClassForm,
)
from classes.constants import ENUMS_IDS, ProductsConsts



class MainPageTemplateView(
    CommonContextMixin,
    TemplateView,
):
    """Представление для главной страницы
    """
    template_name = "classes/index.html"


class CategoryClassesListView(
    CommonContextMixin,
    ListView,
):
    """Представление для категории изделия(болты, гайки, кронштейны)
    """
    template_name = "classes/category.html"
    model = ClassStruct
    context_object_name = "classes"

    def get_queryset(self):
        class_id = self.kwargs.get("class_id")
        try:
            cls = ClassStruct.objects.get(pk=class_id)
            classes = ClassStruct.objects.filter(main_class=cls).order_by("id")
            return classes
        except ClassStruct.DoesNotExist:
            raise Http404(f"Класса с ID={class_id} не существует")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get("class_id")
        main_class = ClassStruct.objects.get(pk=class_id)
        context["main_class"] = main_class
        return context


class ProdClassCreateView(
    CommonContextMixin,
    CreateView,
):
    """Представление для создания нового класса изделия
    """
    form_class = ProdClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/prod_class.html"


class EnumClassCreateView(
    CommonContextMixin,
    CreateView,
):
    """Представление для создания нового класса перечисления
    """
    form_class = EnumClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/enum_class.html"


class ClassUpdateView(
    CommonContextMixin,
    UpdateView,
):
    """Представление для изменения экземпляра класса
    """
    def get_object(self):
        class_id = self.kwargs.get("class_id")
        class_ = ClassStruct.objects.get(pk=class_id)
        return class_

    def get_template_names(self):
        class_id = self.kwargs.get("class_id")
        class_ = ClassStruct.objects.get(pk=class_id)
        if class_.main_class.pk in ENUMS_IDS:
            return ["classes/enum_class.html"]
        return ["classes/prod_class.html"]

    def get_form_class(self):
        class_id = self.kwargs.get("class_id")
        class_ = ClassStruct.objects.get(pk=class_id)
        if class_.main_class.pk in ENUMS_IDS:
            return EnumClassForm
        return ProdClassForm

    def get_success_url(self):
        class_id = self.kwargs.get("class_id")
        class_ = ClassStruct.objects.get(pk=class_id)
        return reverse_lazy(
            "classes:category_classes",
            kwargs={
                "class_id": class_.main_class.pk,
            },
        )


def delete(
    request: HttpRequest,
    class_id: int,
) -> HttpResponse:
    """Представление для удаления класса
    """
    fastener_classes = ClassStruct.objects.filter(main_class__pk=ProductsConsts.FASTENER_ID)
    class_ = ClassStruct.objects.get(pk=class_id)
    context = {
        "fastener_classes": fastener_classes,
        "instance": class_,
    }
    if request.method == "POST":
        main_class_id = class_.main_class.pk
        ClassStruct.delete_class_and_descendants(class_id)
        return redirect("classes:category_classes", class_id=main_class_id)
    return render(
        request,
        "classes/enum_class.html",
        context,
    )


class ClassParamsListView(
    CommonContextMixin,
    ListView,
):
    """Представление для вывода списка параметров класса
    """
    template_name = "classes/params.html"
    context_object_name = "params"

    def get_queryset(self):
        class_id = self.kwargs.get("class_id")
        params = ParClass.objects.filter(
            class_field=class_id,
        ).order_by("num")
        return params

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get("class_id")
        class_ = ClassStruct.objects.get(
            pk=class_id,
        )
        context["class"] = class_
        return context


class ClassParamCreateView(
    CommonContextMixin,
    CreateView,
):
    """Представление для добавления нового параметра класса
    """
    template_name = "classes/param_class.html"
    form_class = ParClassForm
    context_object_name = "instance"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_ = ClassStruct.objects.get(pk=self.kwargs.get("class_id"))
        context["instance"] = class_
        return context

    def get_success_url(self):
        return reverse_lazy(
            "classes:params_list",
            kwargs={"class_id": self.kwargs.get("class_id")},
        )


class ClassParamUpdateView(
    CommonContextMixin,
    UpdateView
):
    template_name = "classes/param_class.html"
    form_class = ParClassForm
    context_object_name = "instance"

    def get_object(self):
        class_id = self.kwargs.get("class_id")
        param_id = self.kwargs.get("param_id")
        return ParClass.objects.get(
            class_field=class_id,
            parametr=param_id,
        )

    def get_success_url(self):
        return reverse_lazy(
            "classes:params_list",
            kwargs={
                "class_id": self.kwargs.get("class_id")
            }
        )


class ClassParamDeleteView(
    CommonContextMixin,
    DeleteView
):
    model = ParClass
    template_name = "classes/param_class.html"
    context_object_name = "instance"

    def get_object(self):
        return ParClass.objects.get(
            class_field=self.kwargs.get("class_id"),
            parametr=self.kwargs.get("param_id"),
        )

    def get_success_url(self):
        return reverse_lazy(
            "classes:params_list",
            args=[self.kwargs.get("class_id")]
        )


class ChangeParClassNumView(
    CommonContextMixin,
    FormView
):
    model = ParClass
    template_name = "classes/change_num.html"
    form_class = ChangeParClassNumForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance"] = ClassStruct.objects.get(pk=self.kwargs.get("class_id"))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["class_id"] = self.kwargs.get("class_id")
        return kwargs

    def form_valid(self, form):
        return redirect("classes:params_list", class_id=self.kwargs.get("class_id"))
