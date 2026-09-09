from django.views.generic import CreateView, UpdateView, DetailView
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


class EASUpdateView(
    CommonContextMixin,
    UpdateView
):
    model = EconomicActivitySubject
    template_name = "route_tech/eas.html"
    form_class = EconomicActivitySubjectForm
    pk_url_kwarg = "eas_id"

    def get_success_url(self):
        pk = self.get_object().pk
        return reverse_lazy(
            "route_tech:detail_eas",
            kwargs={
                "eas_id": pk,
            },
        )


class EASDetailView(
    CommonContextMixin,
    DetailView
):
    model = EconomicActivitySubject
    pk_url_kwarg = "eas_id"
    template_name = "route_tech/eas.html"
