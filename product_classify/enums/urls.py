from django.urls import path

from . import views


app_name = 'enums'

urlpatterns = [
    path(
        'enums/<int:class_id>/',
        views.enums_list,
        name='enums_list',
    ),
    path(
        'enums/<int:class_id>/<int:enum_id>/',
        views.enums_detail,
        name='enums_detail',
    ),
    path(
        'enums/add/',
        views.add_enum,
        name='add_enum',
    ),
    path(
        'enums/<int:class_id>/<int:enum_id>/edit/',
        views.edit_enum,
        name='edit_enum'
    ),
    path(
        'enums/<int:class_id>/<int:enum_id>/delete/',
        views.delete_enum,
        name='delete_enum',
    ),
    path(
        'enums/change_enum/num/',
        views.change_num,
        name='change_num',
    ),
]
