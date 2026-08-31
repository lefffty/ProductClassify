from django.urls import path

from . import views

app_name = "classes"

urlpatterns = [
    path(
        "",
        views.MainPageTemplateView.as_view(),
        name="index",
    ),
    path(
        "<int:class_id>/",
        views.CategoryClassesListView.as_view(),
        name="category_classes",
    ),
    path(
        "add_prod_class/",
        views.ProdClassCreateView.as_view(),
        name="add_prod_class",
    ),
    path(
        "add_enum_class/",
        views.EnumClassCreateView.as_view(),
        name="add_enum_class",
    ),
    path(
        "<int:class_id>/edit/",
        views.ClassUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<int:class_id>/delete/",
        views.ClassDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<int:class_id>/params/",
        views.ClassParamsListView.as_view(),
        name="params_list",
    ),
    path(
        "<int:class_id>/params/add/",
        views.ClassParamCreateView.as_view(),
        name="add_param",
    ),
    path(
        "<int:class_id>/params/<int:param_id>/edit/",
        views.ClassParamUpdateView.as_view(),
        name="edit_param",
    ),
    path(
        "<int:class_id>/params/<int:param_id>/delete/",
        views.ClassParamDeleteView.as_view(),
        name="delete_param",
    ),
    path(
        "change_num/<int:class_id>/",
        views.ChangeParClassNumView.as_view(),
        name="change_num",
    ),
]
