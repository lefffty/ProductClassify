from django.urls import path, include

from . import views


app_name = "route_tech"

eas_patterns = [
    path("eas/add/", views.EASCreateView.as_view(), name="add_eas"),
]


urlpatterns = eas_patterns