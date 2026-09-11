from django.urls import path, include

from . import views

app_name = "route_tech"

eas_patterns = [
    path("add/", views.EASCreateView.as_view(), name="add_eas"),
    path("edit/<int:eas_id>/", views.EASUpdateView.as_view(), name="edit_eas"),
    path("<int:eas_id>/", views.EASDetailView.as_view(), name="detail_eas"),
    path("delete/<int:eas_id>/", views.EASDeleteView.as_view(), name="delete_eas"),
]

gwc_patterns = [
    path("add/", views.GWCCreateView.as_view(), name="add_gwc"),
    path("edit/<int:gwc_id>/", views.GWCUpdateView.as_view(), name="edit_gwc"),
    path("<int:gwc_id>/", views.GWCDetailView.as_view(), name="detail_gwc"),
    path("delete/<int:gwc_id>/", views.GWCDeleteView.as_view(), name="delete_gwc"),
]

prod_operation_patterns = [
    path("add/", views.ProdOperationCreateView.as_view(), name="add_prod_operation"),
    path(
        "delete/<int:prod_oper_id>/",
        views.ProdOperationDeleteView.as_view(),
        name="delete_prod_operation",
    ),
    path(
        "edit/<int:prod_oper_id>/",
        views.ProdOperationUpdateView.as_view(),
        name="edit_prod_operation",
    ),
    path(
        "<int:prod_oper_id>/",
        views.ProdOperationDetailView.as_view(),
        name="detail_prod_operation",
    ),
]


urlpatterns = [
    path("eas/", include(eas_patterns)),
    path("gwc/", include(gwc_patterns)),
    path("prod_oper/", include(prod_operation_patterns)),
]
