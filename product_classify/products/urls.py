from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path(
        "<int:main_class_id>/<int:class_id>/products/",
        views.class_products,
        name="class_products",
    ),
    path(
        "<int:product_id>/",
        views.ProductDetailView.as_view(),
        name="detail",
    ),
    path(
        "add/",
        views.ProductCreateView.as_view(),
        name="add",
    ),
    path(
        "<int:prod_id>/edit/",
        views.ProductUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<int:prod_id>/delete/",
        views.ProductDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<int:prod_id>/param/<int:param_id>/delete/",
        views.ProductParamDeleteView.as_view(),
        name="delete_param",
    ),
    path(
        "<int:prod_id>/param/<int:param_id>/edit/",
        views.ProductParamUpdateView.as_view(),
        name="edit_param",
    ),
    path(
        "<int:prod_id>/param/add/",
        views.ProductParamCreateView.as_view(),
        name="add_param",
    ),
]
