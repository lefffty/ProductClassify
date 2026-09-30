from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (
    FormView,
    ListView,
    UpdateView,
    CreateView,
    DeleteView,
    TemplateView,
)

from core.mixins import (
    CommonContextMixin,
    HandbookExecutiveRequiredMixin
)

from classes.models import (
    ClassStruct,
    ParClass,
)
from classes.selectors import ClassificatorSelector, ParClassSelector
from classes.forms import (
    EconomicActivitySubjectClassForm,
    ProfessionClassForm,
    QualificationClassForm,
    MeansOfLaborClassForm,
    ChangeParClassNumForm,
    OperationClassForm,
    ProdClassForm,
    EnumClassForm,
    ParClassForm,
)
from classes.constants import ENUMS_IDS


class MainPageTemplateView(
    CommonContextMixin,
    TemplateView,
):
    """Представление для главной страницы"""

    template_name = "classes/index.html"


class CategoryClassesListView(
    PermissionRequiredMixin,
    CommonContextMixin,
    ListView,
):
    """Представление для категории изделия(болты, гайки, кронштейны)"""

    permission_required = "classes.view_classstruct"
    template_name = "classes/category.html"
    model = ClassStruct
    context_object_name = "classes"

    def get_queryset(self):
        self.class_id = self.kwargs.get("class_id")
        self.cls_ = get_object_or_404(ClassStruct, pk=self.class_id)
        return ClassificatorSelector.category_classes_list(self.cls_)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["main_class"] = self.cls_
        return context


class ProdClassCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    CreateView,
):
    """Представление для создания нового класса изделия"""

    form_class = ProdClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/prod_class.html"


class EnumClassCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    CreateView,
):
    """Представление для создания нового класса перечисления"""

    form_class = EnumClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/enum_class.html"


class OperationClassCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    CreateView
):
    form_class = OperationClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/operation_class.html"


class EconomicSubjectActivityClassCreateView(
    CommonContextMixin,
    CreateView
):
    form_class = EconomicActivitySubjectClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/eas_class.html"


class QualificationClassCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin, 
    CreateView
):
    form_class = QualificationClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/qualification_class.html"


class ProfessionClassCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin, 
    CreateView
):
    form_class = ProfessionClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/profession_class.html"


class MeansOfLaborClassCreateView(
    CommonContextMixin,
    CreateView,
):
    form_class = MeansOfLaborClassForm
    success_url = reverse_lazy("classes:index")
    template_name = "classes/mol_class.html"


class ClassUpdateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    UpdateView,
):
    """Представление для изменения экземпляра класса"""

    pk_url_kwarg = "class_id"

    def get_object(self) -> ClassStruct:
        class_id = self.kwargs.get("class_id")
        return ClassificatorSelector.fetch_detail_info(class_id)
    
    def get_template_names(self):
        if self.object.main_class_id in ENUMS_IDS:
            return ["classes/enum_class.html"]
        return ["classes/prod_class.html"]

    def get_form_class(self):
        if self.object.main_class_id in ENUMS_IDS:
            return EnumClassForm
        return ProdClassForm

    def get_success_url(self):
        return reverse_lazy(
            "classes:category_classes",
            kwargs={
                "class_id": self.object.main_class_id,
            },
        )


class ClassDeleteView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin, 
    DeleteView
):
    template_name = "classes/enum_class.html"
    context_object_name = "instance"

    def get_object(self) -> ClassStruct:
        class_id = self.kwargs.get("class_id")
        return ClassificatorSelector.fetch_detail_info(class_id)

    def get_success_url(self):
        return reverse_lazy(
            "classes:category_classes",
            kwargs={
                "class_id": self.object.main_class_id,
            },
        )


class ClassParamsListView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    ListView,
):
    """Представление для вывода списка параметров класса"""

    template_name = "classes/params.html"
    context_object_name = "params"

    def get_queryset(self):
        class_id = self.kwargs.get("class_id")
        return ParClassSelector.fetch_parclass_list(class_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get("class_id")
        context["class"] = ClassificatorSelector.fetch_detail_info(class_id)
        return context


class ClassParamCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    CreateView,
):
    """Представление для добавления нового параметра класса"""

    template_name = "classes/param_class.html"
    form_class = ParClassForm
    context_object_name = "instance"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get("class_id")
        class_ = get_object_or_404(ClassStruct, pk=class_id)
        context["instance"] = class_
        return context

    def get_success_url(self):
        return reverse_lazy(
            "classes:params_list",
            kwargs={"class_id": self.kwargs.get("class_id")},
        )


class ClassParamUpdateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin, 
    UpdateView
):
    template_name = "classes/param_class.html"
    form_class = ParClassForm
    context_object_name = "instance"

    def get_object(self):
        class_id = self.kwargs.get("class_id")
        param_id = self.kwargs.get("param_id")
        return ParClassSelector.fetch_by_ids(class_id, param_id)

    def get_success_url(self):
        return reverse_lazy(
            "classes:params_list", kwargs={"class_id": self.kwargs.get("class_id")}
        )


class ClassParamDeleteView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin, 
    DeleteView
):
    model = ParClass
    template_name = "classes/param_class.html"
    context_object_name = "instance"

    def get_object(self):
        class_id = self.kwargs.get("class_id")
        param_id = self.kwargs.get("param_id")
        return ParClassSelector.fetch_by_ids(class_id, param_id)

    def get_success_url(self):
        return reverse_lazy("classes:params_list", args=[self.kwargs.get("class_id")])


class ChangeParClassNumView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin, 
    FormView
):
    model = ParClass
    template_name = "classes/change_num.html"
    form_class = ChangeParClassNumForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get("class_id")
        context["instance"] = get_object_or_404(ClassStruct, pk=class_id)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["class_id"] = self.kwargs.get("class_id")
        return kwargs

    def form_valid(self, _):
        return redirect("classes:params_list", class_id=self.kwargs.get("class_id"))
