from django.urls import path

from . import views

app_name = "enums"

urlpatterns = [
    path(
        "<int:class_id>/",
        views.EnumsListView.as_view(),
        name="list",
    ),
    path(
        "<int:class_id>/<int:enum_id>/",
        views.EnumsDetailView.as_view(),
        name="detail",
    ),
    path(
        "add/",
        views.EnumsCreateView.as_view(),
        name="add",
    ),
    path(
        "<int:class_id>/<int:enum_id>/edit/",
        views.EnumsUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<int:class_id>/<int:enum_id>/delete/",
        views.EnumsDeleteView.as_view(),
        name="delete",
    ),
    path(
        "change_enum/num/",
        views.ChangeEnumsNumView.as_view(),
        name="change_num",
    ),
]
