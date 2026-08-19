from django.http import HttpRequest, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.forms import inlineformset_factory

from loguru import logger

from classes.models import ClassStruct
from classes.constants import ProductsConsts

from specifications.constants import FormsetConsts
from specifications.models import ProdComponent, Prod, SpecificationLogs
from specifications.forms import ProdComponentForm
from specifications.utils import (
    create_total_cost_ratio_pdf,
    create_change_log_pdf,
    save_formset_with_logging
)

ProdComponentFormSet = inlineformset_factory(
    Prod,
    ProdComponent,
    form=ProdComponentForm,
    fk_name="parent_prod",
    fields=('component', 'quantity',),
    extra=1,
    can_delete=True,
)


def get_total_cost_ratio_view(request: HttpRequest, product_id: int):
    try:
        raw_quantity = request.GET.get("quantity")
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        quantity = 1

    results = ProdComponent.total_cost_ratio(product_id, quantity)

    product = Prod.objects.get(pk=product_id)

    buffer = create_total_cost_ratio_pdf(results, product)

    filename = f"Спецификация_изделия_{product.name}.pdf"

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf"
    )


def get_product_changelog_view(_: HttpRequest, product_id: int):
    results = SpecificationLogs.get_changelog(product_id)

    product = Prod.objects.get(pk=product_id)

    buffer = create_change_log_pdf(results)

    filename = f"История_изменений_спецификации_изделия_{product.name}.pdf"

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )


def edit_specification_view(request: HttpRequest, product_id: int):
    product = get_object_or_404(Prod, pk=product_id)
    edit_mode = request.GET.get('edit') == '1'
    fastener_classes = ClassStruct.objects.filter(main_class__exact=ProductsConsts.FASTENER_ID)

    if request.method == 'POST':
        formset = ProdComponentFormSet(request.POST, instance=product)
        if formset.is_valid():
            with transaction.atomic():
                save_formset_with_logging(formset, product)
            return redirect('products:detail', product_id=product_id)
        else:
            logger.info(formset.errors)
    else:
        formset = ProdComponentFormSet(instance=product)
        if not edit_mode:
            for form in formset:
                for field in form.fields.values():
                    field.disabled = True
            # Отключаем добавление/удаление в режиме просмотра
            formset.extra = FormsetConsts.EXTRA
            formset.can_delete = False

    return render(request, 'products/prodcomponent_edit.html', {
        "fastener_classes": fastener_classes,
        "formset": formset,
        "product": product,
        "edit_mode": edit_mode,
    })
