from django.shortcuts import (
    render,
    redirect,
)
from django.urls import reverse_lazy
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.db.models import Q
from django.views.generic import (
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.views import RedirectURLMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import ContextMixin

from classes.models import (
    ClassStruct,
    ParClass,
)
from .forms import (
    ProdForm,
    ParProdForm,
    SearchForm,
)
from .models import (
    Prod,
    ParProd,
)
from .constants import (
    FASTENER_ID
)


class CommonContextMixin(
    ContextMixin
):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(
            main_class__exact=FASTENER_ID
        )
        context['fastener_classes'] = fastener_classes
        return context


def class_products(
    request: HttpRequest,
    main_class_id: int,
    class_id: int,
) -> HttpResponse:
    """
    Страница списка изделий
    """
    main_cls = ClassStruct.objects.get(
        pk=main_class_id,
    )
    cls = ClassStruct.objects.get(
        pk=class_id,
    )
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )

    base_query = Q(prod__class_field__exact=class_id)

    search_form = SearchForm(
        request.GET,
        cls=ClassStruct.objects.get(
            pk=class_id,
        ),
    )

    if search_form.is_valid():
        data = search_form.cleaned_data
        filter_queries = []
        for par_class in ParClass.objects.filter(
            class_field__exact=class_id,
        ):
            if par_class.parametr.name in data and data[par_class.parametr.name] is not None:
                if par_class.parametr.parametr_type.id in [15, 16, 18, 19]:
                    filter_queries.append(
                        Q(par=par_class.parametr) &
                        Q(enum_val__exact=data[par_class.parametr.name])
                    )
                elif par_class.parametr.parametr_type.id in [27, 28]:
                    mn_val = data[par_class.parametr.name][0]
                    mx_val = data[par_class.parametr.name][1]

                    if mn_val is not None and mx_val is not None:
                        try:
                            if par_class.parametr.parametr_type.id == 27:
                                mn_val = float(mn_val)
                                mx_val = float(mx_val)
                                filter_queries.append(
                                    Q(par=par_class.parametr) &
                                    Q(double_value__gte=mn_val) &
                                    Q(double_value__lte=mx_val)
                                )
                            elif par_class.parametr.parametr_type.id == 28:
                                mn_val = int(mn_val)
                                mx_val = int(mx_val)
                                filter_queries.append(
                                    Q(par=par_class.parametr) &
                                    Q(int_value__gte=mn_val) &
                                    Q(int_value__lte=mx_val)
                                )
                        except (ValueError, TypeError):
                            continue

        if filter_queries:
            products = ParProd.objects.filter(base_query)

            matching_products = []
            for filter_query in filter_queries:
                matching_products.append(
                    set(products.filter(filter_query).values_list(
                        'id', flat=True))
                )

            if matching_products:
                common_product_ids = set.intersection(*matching_products)
                products = ParProd.objects.filter(
                    id__in=common_product_ids)
            else:
                products = ParProd.objects.none()
        else:
            products = ParProd.objects.filter(base_query)

    else:
        products = ParProd.objects.filter(base_query)

    products_no_params = Prod.objects.exclude(
        product_params__isnull=False,
    ).filter(
        class_field__exact=class_id
    )
    products = products.distinct('prod')

    context = {
        'id': class_id,
        'main_class_id': main_class_id,
        'search_form': search_form,
        'products': products,
        'products_no_params': products_no_params,
        'main_cls': main_cls,
        'cls': cls,
        'prod_count': products.count(),
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'products/list.html',
        context,
    )


class ProductDetailView(
    DetailView,
    CommonContextMixin,
):
    model = Prod
    template_name = 'products/detail.html'
    pk_url_kwarg = 'product_id'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod = self.get_object()
        context['params'] = ParProd.objects.filter(prod=prod)
        return context


class ProductCreateView(
    CreateView,
    CommonContextMixin,
):
    template_name = 'products/product.html'
    model = Prod
    form_class = ProdForm
    success_url = reverse_lazy('classes:index')


class ProductUpdateView(
    UpdateView,
    CommonContextMixin,
):
    template_name = 'products/product.html'
    pk_url_kwarg = 'prod_id'
    form_class = ProdForm
    context_object_name = 'instance'
    model = Prod

    def get_success_url(self):
        prod_id = self.kwargs.get('prod_id')
        return reverse_lazy(
            'products:product_detail',
            kwargs={
                'product_id': prod_id,
            },
        )


class ProductDeleteView(
    DeleteView,
    CommonContextMixin,
):
    template_name = 'products/product.html'
    model = Prod
    context_object_name = 'instance'
    pk_url_kwarg = 'prod_id'

    def get_success_url(self):
        prod_id = self.kwargs.get('prod_id')
        product = Prod.objects.get(pk=prod_id)
        class_id = product.class_field.pk
        main_class_id = product.class_field.main_class.pk
        return reverse_lazy(
            'products:class_products',
            kwargs={
                'main_class_id': main_class_id,
                'class_id': class_id,
            }
        )


class ProductParamSuccessURL(
    RedirectURLMixin,
):
    def get_success_url(self):
        prod_id = self.kwargs.get('prod_id')
        return reverse_lazy(
            'products:product_detail',
            kwargs={
                'product_id': prod_id,
            }
        )


class ProductParamSingleObject(
    SingleObjectMixin,
):
    def get_object(self):
        prod_id = self.kwargs.get('prod_id')
        param_id = self.kwargs.get('param_id')
        instance = ParProd.objects.get(
            prod=prod_id,
            par=param_id,
        )
        return instance


class ProductParamUpdateView(
    ProductParamSuccessURL,
    ProductParamSingleObject,
    CommonContextMixin,
    UpdateView,
):
    form_class = ParProdForm
    context_object_name = 'instance'
    template_name = 'products/prodparam.html'


class ProductParamDeleteView(
    ProductParamSuccessURL,
    ProductParamSingleObject,
    CommonContextMixin,
    DeleteView,
):
    model = ParProd
    template_name = 'products/prodparam.html'
    context_object_name = 'instance'


class ProductParamCreateView(
    ProductParamSuccessURL,
    CommonContextMixin,
    CreateView,
):
    template_name = 'products/prodparam.html'
    form_class = ParProdForm
    model = ParProd

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod_id = self.kwargs.get('prod_id')
        product = Prod.objects.get(pk=prod_id)
        context['instance'] = product
        return context
