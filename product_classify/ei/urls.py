from django.urls import path

from . import views


app_name = 'ei'

urlpatterns = [
    path(
        'ei/',
        views.EiListView.as_view(),
        name='ei_list',
    ),
    path(
        'ei/add/',
        views.add_ei,
        name='add_ei',
    ),
    path(
        'ei/<int:ei_id>/',
        views.EiDetailView.as_view(),
        name='ei_detail',
    ),
    path(
        'ei/<int:ei_id>/edit/',
        views.edit_ei,
        name='edit_ei',
    ),
    path(
        'ei/<int:ei_id>/delete/',
        views.delete_ei,
        name='delete_ei',
    ),
]
