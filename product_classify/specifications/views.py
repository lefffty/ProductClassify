from django.http import HttpRequest, FileResponse

from specifications.models import ProdComponent, Prod
from specifications.utils import create_total_cost_ratio_pdf


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
