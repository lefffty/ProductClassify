from django.views.generic import CreateView
from django.urls import reverse_lazy

from core.mixins import CommonContextMixin

from route_tech.forms import EconomicActivitySubjectForm
from route_tech.models import EconomicActivitySubject


class EASCreateView(
    CommonContextMixin,
    CreateView
):
    template_name = "route_tech/eas.html"
    model = EconomicActivitySubject
    form_class = EconomicActivitySubjectForm
    success_url = reverse_lazy("classes:index")
