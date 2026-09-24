from django.http import HttpRequest, FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction

from loguru import logger

from core.decorators import roles_required

from accounts.constants import RoleCodes

from core.views import get_context_data
from specifications.forms import ProdComponentFormSet
from specifications.constants import FormsetConsts
from specifications.models import ProdComponent, Prod, SpecificationLogs
from specifications.utils import (
    create_total_cost_ratio_pdf,
    create_change_log_pdf,
    save_formset_with_logging,
    get_changelog_filename,
    get_total_cost_ratio_filename,
)


@roles_required(RoleCodes.BUILDER)
def get_total_cost_ratio_view(request: HttpRequest, product_id: int) -> FileResponse:
    try:
        raw_quantity = request.GET.get("quantity")
        quantity = int(raw_quantity)
    except TypeError, ValueError:
        quantity = 1

    results = ProdComponent.total_cost_ratio(product_id, quantity)

    product = get_object_or_404(Prod, pk=product_id)

    buffer = create_total_cost_ratio_pdf(results, product)

    filename = get_total_cost_ratio_filename(product.name)

    return FileResponse(
        buffer, as_attachment=True, filename=filename, content_type="application/pdf"
    )


@roles_required(RoleCodes.BUILDER)
def get_product_changelog_view(_: HttpRequest, product_id: int) -> FileResponse:
    results = SpecificationLogs.get_changelog(product_id)

    product = get_object_or_404(Prod, pk=product_id)

    buffer = create_change_log_pdf(results)

    filename = get_changelog_filename(product.name)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )


@roles_required(RoleCodes.BUILDER)
def edit_specification_view(request: HttpRequest, product_id: int) -> HttpResponse:
    context = get_context_data()
    product = get_object_or_404(Prod, pk=product_id)
    edit_mode = request.GET.get("edit") == "1"

    if request.method == "POST":
        formset = ProdComponentFormSet(request.POST, instance=product)
        if formset.is_valid():
            with transaction.atomic():
                save_formset_with_logging(formset, product)
            return redirect("products:detail", product_id=product_id)
        else:
            logger.info(formset.errors)
    else:
        formset = ProdComponentFormSet(instance=product)
        if not edit_mode:
            for form in formset:
                for field in form.fields.values():
                    field.disabled = True
            formset.extra = FormsetConsts.EXTRA
            formset.can_delete = False

    context.update({
        "formset": formset,
        "product": product,
        "edit_mode": edit_mode,
    })

    return render(
        request,
        "products/prodcomponent_edit.html",
        context=context,
    )
