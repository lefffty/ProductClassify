from django.urls import path

from . import views


app_name = 'parametr'

urlpatterns = [
    path(
        'parameters/list/',
        views.parametr_list,
        name='parametr_list'
    ),
    path(
        'parameters/<int:parametr_id>/',
        views.parametr_detail,
        name='parametr_detail',
    ),
    path(
        'parameters/add/',
        views.add_parametr,
        name='add_parametr',
    ),
    path(
        'parameters/<int:parametr_id>/edit/',
        views.edit_parametr,
        name='edit_parametr',
    ),
    path(
        'parameters/<int:parametr_id>/delete/',
        views.delete_parametr,
        name='delete_parametr',
    ),
]
