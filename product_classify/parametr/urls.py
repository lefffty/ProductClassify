from django.urls import path

from . import views

app_name = "parametr"

urlpatterns = [
    path(
        "list/",
        views.ParametrListView.as_view(),
        name="list",
    ),
    path(
        "<int:parametr_id>/",
        views.ParametrDetailView.as_view(),
        name="detail",
    ),
    path(
        "add/",
        views.ParametrCreateView.as_view(),
        name="add",
    ),
    path(
        "<int:parametr_id>/edit/",
        views.ParametrUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<int:parametr_id>/delete/",
        views.ParametrDeleteView.as_view(),
        name="delete",
    ),
]
