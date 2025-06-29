from django.urls import path

from . import views


app_name = 'parametr'

urlpatterns = [
    path(
        'parameters/list/',
        views.ParametrListView.as_view(),
        name='parametr_list'
    ),
    path(
        'parameters/<int:parametr_id>/',
        views.ParametrDetailView.as_view(),
        name='parametr_detail',
    ),
    path(
        'parameters/add/',
        views.ParametrCreateView.as_view(),
        name='add_parametr',
    ),
    path(
        'parameters/<int:parametr_id>/edit/',
        views.ParametrUpdateView.as_view(),
        name='edit_parametr',
    ),
    path(
        'parameters/<int:parametr_id>/delete/',
        views.ParametrDeleteView.as_view(),
        name='delete_parametr',
    ),
]
