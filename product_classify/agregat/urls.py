from django.urls import path

from . import views

app_name = "agregat"

urlpatterns = [
    path(
        "list/",
        views.AgregatListView.as_view(),
        name="list"
    ),
    path(
        "<int:agregat_id>/",
        views.AgregatDetailView.as_view(),
        name="detail",
    ),
    path(
        "<int:agregat_id>/add/",
        views.AgregatParametrCreateView.as_view(),
        name="add",
    ),
    path(
        "<int:agregat_id>/param/<int:param_id>/delete/",
        views.AgregatParametrDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<int:agregat_id>/change_num/",
        views.change_num,
        name="change_num",
    ),
]
