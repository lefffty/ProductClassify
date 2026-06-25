from django.urls import path

from . import views

app_name = "enums"

urlpatterns = [
    path(
        "enums/<int:class_id>/",
        views.EnumsListView.as_view(),
        name="enums_list",
    ),
    path(
        "enums/<int:class_id>/<int:enum_id>/",
        views.EnumsDetailView.as_view(),
        name="enums_detail",
    ),
    path(
        "enums/add/",
        views.EnumsCreateView.as_view(),
        name="add_enum",
    ),
    path(
        "enums/<int:class_id>/<int:enum_id>/edit/",
        views.EnumsUpdateView.as_view(),
        name="edit_enum",
    ),
    path(
        "enums/<int:class_id>/<int:enum_id>/delete/",
        views.EnumsDeleteView.as_view(),
        name="delete_enum",
    ),
    path(
        "enums/change_enum/num/",
        views.change_num,
        name="change_num",
    ),
]
