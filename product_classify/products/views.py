from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpRequest
from django.db.models import OuterRef
from django.views.generic import (
    FormView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.views import RedirectURLMixin
from django.views.generic.detail import SingleObjectMixin

from classes.constants import ProductsConsts
from classes.models import ClassStruct
from core.mixins import CommonContextMixin

from products.forms import (
    ProdForm,
    ParProdForm,
    SearchForm,
    ModificationForm,
)
from products.utils import get_filtered_products
from products.models import (
    Prod,
    ParProd,
)


def class_products(request: HttpRequest, main_class_id: int, class_id: int):
    main_cls = get_object_or_404(ClassStruct, pk=main_class_id)
    class_ = get_object_or_404(ClassStruct, pk=class_id)

    fastener_classes = ClassStruct.objects.filter(main_class__exact=ProductsConsts.FASTENER_ID)
    search_form = SearchForm(request.GET, cls=class_)

    products_qs = Prod.objects.filter(class_field=class_id)

    if search_form.is_valid():
        form_data = search_form.cleaned_data
        products_qs = get_filtered_products(products_qs, form_data, class_id)

    products_no_params = Prod.objects.filter(class_field=class_id).exclude(
        id__in=ParProd.objects.filter(prod=OuterRef('pk')).values('prod')
    )

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
        "fastener_classes": fastener_classes,
    }
    return render(request, "products/list.html", context)


class ProductDetailView(
    CommonContextMixin,
    DetailView,
):
    model = Prod
    template_name = "products/detail.html"
    pk_url_kwarg = "product_id"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod = self.get_object()
        context["params"] = ParProd.objects.filter(prod=prod)
        return context


class ProductCreateView(
    CommonContextMixin,
    CreateView,
):
    template_name = "products/product.html"
    model = Prod
    form_class = ProdForm
    success_url = reverse_lazy("classes:index")


class ProductUpdateView(
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
    CommonContextMixin,
    DeleteView,
):
    template_name = "products/product.html"
    model = Prod
    context_object_name = "instance"
    pk_url_kwarg = "prod_id"

    def get_success_url(self):
        prod_id = self.kwargs.get("prod_id")
        product = Prod.objects.get(pk=prod_id)
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
        instance = ParProd.objects.get(
            prod=prod_id,
            par=param_id,
        )
        return instance


class ProductParamUpdateView(
    ProductParamSuccessURL,
    CommonContextMixin,
    ProductParamSingleObject,
    UpdateView,
):
    form_class = ParProdForm
    context_object_name = "instance"
    template_name = "products/prodparam.html"


class ProductParamDeleteView(
    ProductParamSuccessURL,
    ProductParamSingleObject,
    CommonContextMixin,
    DeleteView,
):
    model = ParProd
    template_name = "products/prodparam.html"
    context_object_name = "instance"


class ProductParamCreateView(
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
        product = Prod.objects.get(pk=prod_id)
        context["instance"] = product
        return context


class ModificationCreateView(
    CommonContextMixin,
    FormView
):
    template_name = "products/modification.html"
    form_class = ModificationForm

    def form_valid(self, form: ModificationForm):
        cleaned_data = form.cleaned_data
        name = cleaned_data.get("name")
        short_name = cleaned_data.get("short_name")
        modification = Prod.create_modification(
            self.kwargs.get("product_id"),
            name,
            short_name
        )
        modification_id = modification.modification_id
        return redirect(
            "products:detail",
            product_id=modification_id
        )
