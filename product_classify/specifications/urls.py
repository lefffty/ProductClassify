from django.urls import path

from . import views


app_name = "specifications"

urlpatterns = [
    path(
        "<int:product_id>/total_cost_ratio",
        views.get_total_cost_ratio_view,
        name="total_cost_ratio",
    ),
    path(
        "<int:product_id>/changelog",
        views.get_product_changelog_view,
        name="changelog",
    ),
]
