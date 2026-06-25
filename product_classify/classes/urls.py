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
        name="edit_class",
    ),
    path(
        "<int:class_id>/delete/",
        views.delete_class,
        name="delete_class",
    ),
    path(
        "<int:class_id>/params/",
        views.ClassParamsListView.as_view(),
        name="class_params_list",
    ),
    path(
        "<int:class_id>/params/add/",
        views.ClassParamCreateView.as_view(),
        name="add_param_class",
    ),
    path(
        "<int:class_id>/params/<int:param_id>/edit/",
        views.edit_param_class,
        name="edit_param_class",
    ),
    path(
        "<int:class_id>/params/<int:param_id>/delete/",
        views.delete_param_class,
        name="delete_param_class",
    ),
    path(
        "change_parclass_num/<int:class_id>/",
        views.change_parclass_num,
        name="change_parclass_num",
    ),
]
