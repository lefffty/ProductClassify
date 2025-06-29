from django.shortcuts import (
    render,
    redirect,
)
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.db.models import Q

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
        parprod__isnull=False,
    ).filter(
        class_field__exact=class_id
    )
    products = products.distinct('prod')

    context = {
        'class_id': class_id,
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


def product_detail(
    request: HttpRequest,
    product_id: int,
) -> HttpResponse:
    """
    Страница изделия
    """
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    product = Prod.objects.get(pk=product_id)
    params = ParProd.objects.filter(
        prod=product_id
    )
    context = {
        'product': product,
        'params': params,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'products/detail.html',
        context
    )


def add_product(
    request: HttpRequest,
) -> HttpResponse:
    """
    Добавление изделия
    """
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    if request.method == 'POST':
        form = ProdForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('classes:index')
    else:
        form = ProdForm()
    context = {
        'form': form,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'products/product.html',
        context
    )


def edit_product(
    request: HttpRequest,
    prod_id: int,
) -> HttpResponse:
    """
    Редактирование изделия
    """
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    instance = Prod.objects.get(pk=prod_id)
    form = ProdForm(
        request.POST or None,
        instance=instance,
    )
    if form.is_valid():
        form.save(commit=True)
        return redirect('products:product_detail', prod_id)
    context = {
        'form': form,
        'instance': instance,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'products/product.html',
        context,
    )


def delete_product(
    request: HttpRequest,
    prod_id: int,
) -> HttpResponse:
    """
    Удаление изделия
    """
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    instance = Prod.objects.get(pk=prod_id)
    main_class_id = ClassStruct.objects.get(
        class_id__exact=instance.class_field.id
    ).main_class.id
    if request.method == 'POST':
        instance.delete()
        return redirect(
            'products:class_products',
            main_class_id,
            instance.class_field.id,
        )
    context = {
        'instance': instance,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'products/product.html',
        context,
    )


def edit_param_from_product(
    request: HttpRequest,
    prod_id: int,
    param_id: int,
) -> HttpResponse:
    """
    Редактирование параметра изделия
    """
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    instance = ParProd.objects.get(
        prod=prod_id,
        par=param_id,
    )
    form = ParProdForm(
        request.POST or None,
        instance=instance,
    )
    if form.is_valid():
        form.save(commit=True)
        return redirect(
            'products:product_detail',
            prod_id,
        )
    context = {
        'instance': instance,
        'form': form,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'products/prodparam.html',
        context,
    )


def delete_param_from_product(
    request: HttpRequest,
    prod_id: int,
    param_id: int,
) -> HttpResponse:
    """
    Удаление параметра из изделия
    """
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    instance = ParProd.objects.get(
        prod=prod_id,
        par=param_id,
    )
    if request.method == 'POST':
        instance.delete()
        return redirect('products:product_detail', prod_id)
    context = {
        'instance': instance,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'products/prodparam.html',
        context,
    )


def add_param_to_product(
    request: HttpRequest,
    prod_id: int,
) -> HttpResponse:
    """
    Добавление параметра в изделие
    """
    fastener_classes = ClassStruct.objects.filter(
        main_class__exact=FASTENER_ID
    )
    instance = Prod.objects.get(pk=prod_id)
    if request.method == 'POST':
        form = ParProdForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect(
                'products:product_detail',
                prod_id,
            )
    else:
        form = ParProdForm(id=prod_id)
    context = {
        'instance': instance,
        'form': form,
        'fastener_classes': fastener_classes,
    }
    return render(
        request,
        'products/prodparam.html',
        context,
    )
