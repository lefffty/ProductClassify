from django.urls import path, include

from . import views


app_name = "route_tech"

eas_patterns = [
    path("eas/add/", views.EASCreateView.as_view(), name="add_eas"),
    path("eas/edit/<int:eas_id>/", views.EASUpdateView.as_view(), name="edit_eas"),
    path("eas/<int:eas_id>/", views.EASDetailView.as_view(), name="detail_eas"),
    path("eas/delete/<int:eas_id>/", views.EASDeleteView.as_view(), name="delete_eas"),
]


urlpatterns = eas_patterns
