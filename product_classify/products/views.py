from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import RedirectURLMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import (
    FormView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from classes.models import ClassStruct

from core.mixins import (
    CommonContextMixin,
    BuilderRequiredMixin,
    HandbookExecutiveRequiredMixin,
)
from core.views import get_context_data

from products.services import ProdService
from products.forms import (
    ProdForm,
    ParProdForm,
    SearchForm,
    ModificationForm,
)
from products.selectors import ParProdSelector, ProdSelector
from products.models import (
    Prod,
    ParProd,
)
from specifications.forms import TotalCostRatioForm


@login_required
@permission_required("products.view_prod", raise_exception=True)
def class_products(request: HttpRequest, main_class_id: int, class_id: int):
    main_cls = get_object_or_404(ClassStruct, pk=main_class_id)

    class_ = get_object_or_404(
        ClassStruct.objects.select_related("main_class"), pk=class_id
    )

    base_qs = ProdSelector.fetch_base_queryset(class_id)

    products_qs = base_qs

    search_form = SearchForm(request.GET, cls=class_)

    if search_form.is_valid():
        form_data = search_form.cleaned_data
        products_qs = ProdSelector.get_filtered_products(products_qs, form_data, class_id)

    products_no_params = ProdSelector.annotate_filtered_products(base_qs)

    prod_count = products_qs.count() + products_no_params.count()

    context = {
        "id": class_id,
        "main_class_id": main_class_id,
        "search_form": search_form,
        "products": products_qs,
        "products_no_params": products_no_params,
        "main_cls": main_cls,
        "cls": class_,
        "prod_count": prod_count,
    }
    context.update(get_context_data())
    return render(request, "products/list.html", context)


class ProductDetailView(
    PermissionRequiredMixin,
    CommonContextMixin,
    DetailView,
):
    permission_required = "products.view_prod"
    model = Prod
    template_name = "products/detail.html"
    pk_url_kwarg = "product_id"
    context_object_name = "product"

    def get_object(self):
        product_id = self.kwargs.get("product_id")
        return ProdSelector.fetch_by_id(product_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod = self.object
        context["params"] = ProdSelector.fetch_detail_info(prod)
        context["form"] = TotalCostRatioForm(prod.ei)
        return context


class ProductCreateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    CreateView,
):
    template_name = "products/product.html"
    model = Prod
    form_class = ProdForm
    success_url = reverse_lazy("classes:index")


class ProductUpdateView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    UpdateView,
):
    template_name = "products/product.html"
    pk_url_kwarg = "prod_id"
    form_class = ProdForm
    context_object_name = "instance"
    model = Prod

    def get_success_url(self):
        prod_id = self.kwargs.get("prod_id")
        return reverse_lazy(
            "products:detail",
            kwargs={
                "product_id": prod_id,
            },
        )


class ProductDeleteView(
    HandbookExecutiveRequiredMixin,
    CommonContextMixin,
    DeleteView,
):
    template_name = "products/product.html"
    model = Prod
    context_object_name = "instance"
    pk_url_kwarg = "prod_id"

    def get_success_url(self):
        prod_id = self.kwargs.get("prod_id")
        product = get_object_or_404(Prod, pk=prod_id)
        class_id = product.class_field.pk
        main_class_id = product.class_field.main_class.pk
        return reverse_lazy(
            "products:class_products",
            kwargs={
                "main_class_id": main_class_id,
                "class_id": class_id,
            },
        )


class ProductParamSuccessURL(
    RedirectURLMixin,
):
    def get_success_url(self):
        prod_id = self.kwargs.get("prod_id")
        return reverse_lazy(
            "products:detail",
            kwargs={
                "product_id": prod_id,
            },
        )


class ProductParamSingleObject(
    SingleObjectMixin,
):
    def get_object(self):
        prod_id = self.kwargs.get("prod_id")
        param_id = self.kwargs.get("param_id")
        return ParProdSelector.fetch_object_by_ids(prod_id, param_id)


class ProductParamUpdateView(
    HandbookExecutiveRequiredMixin,
    ProductParamSuccessURL,
    CommonContextMixin,
    ProductParamSingleObject,
    UpdateView,
):
    form_class = ParProdForm
    context_object_name = "instance"
    template_name = "products/prodparam.html"


class ProductParamDeleteView(
    HandbookExecutiveRequiredMixin,
    ProductParamSuccessURL,
    ProductParamSingleObject,
    CommonContextMixin,
    DeleteView,
):
    model = ParProd
    template_name = "products/prodparam.html"
    context_object_name = "instance"


class ProductParamCreateView(
    HandbookExecutiveRequiredMixin,
    ProductParamSuccessURL,
    CommonContextMixin,
    CreateView,
):
    template_name = "products/prodparam.html"
    form_class = ParProdForm
    model = ParProd

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod_id = self.kwargs.get("prod_id")
        product = get_object_or_404(Prod, pk=prod_id)
        context["instance"] = product
        return context


class ModificationCreateView(
    BuilderRequiredMixin,
    CommonContextMixin,
    FormView
):
    template_name = "products/modification.html"
    form_class = ModificationForm

    def form_valid(self, form: ModificationForm):
        cleaned_data = form.cleaned_data
        product_id = self.kwargs.get("product_id")
        modification = ProdService.create_modification(product_id, **cleaned_data)
        modification_id = modification.modification_id
        return redirect("products:detail", product_id=modification_id)
