from django.urls import path

from . import views


app_name = 'agregat'

urlpatterns = [
    path(
        'agregat/list/',
        views.AgregatListView.as_view(),
        name='agregat_list'
    ),
    path(
        'agregat/<int:agregat_id>/',
        views.AgregatDetailView.as_view(),
        name='agregat_detail',
    ),
    path(
        'agregat/<int:agregat_id>/add/',
        views.AgregatParametrCreateView.as_view(),
        name='add_parametr_to_agregat',
    ),
    path(
        'agregat/<int:agregat_id>/param/<int:param_id>/delete/',
        views.delete_parametr_from_agregat,
        name='delete_parametr_from_agregat',
    ),
    path(
        'agregat/<int:agregat_id>/change_num/',
        views.change_agregat_num,
        name='change_agregat_num',
    ),
]
