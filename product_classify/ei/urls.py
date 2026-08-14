from django.urls import path

from . import views

app_name = "ei"

urlpatterns = [
    path(
        "list",
        views.EiListView.as_view(),
        name="list",
    ),
    path(
        "add/",
        views.EiCreateView.as_view(),
        name="add",
    ),
    path(
        "<int:ei_id>/",
        views.EiDetailView.as_view(),
        name="detail",
    ),
    path(
        "<int:ei_id>/edit/",
        views.EiUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<int:ei_id>/delete/",
        views.EiDeleteView.as_view(),
        name="delete",
    ),
]
