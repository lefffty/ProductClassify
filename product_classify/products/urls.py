from django.urls import path
from . import views


app_name = 'products'

urlpatterns = [
    path(
        '<int:main_class_id>/<int:class_id>/products/',
        views.class_products,
        name='class_products',
    ),
    path(
        'products/<int:product_id>/',
        views.ProductDetailView.as_view(),
        name='product_detail',
    ),
    path(
        'products/add/',
        views.ProductCreateView.as_view(),
        name='add_product',
    ),
    path(
        'products/<int:prod_id>/edit/',
        views.edit_product,
        name='edit_product',
    ),
    path(
        'products/<int:prod_id>/delete/',
        views.delete_product,
        name='delete_product',
    ),
    path(
        'products/<int:prod_id>/param/<int:param_id>/delete/',
        views.delete_param_from_product,
        name='delete_param_from_product',
    ),
    path(
        'products/<int:prod_id>/param/<int:param_id>/edit/',
        views.edit_param_from_product,
        name='edit_param_from_product',
    ),
    path(
        'products/<int:prod_id>/param/add/',
        views.add_param_to_product,
        name='add_param_to_product',
    ),
]
