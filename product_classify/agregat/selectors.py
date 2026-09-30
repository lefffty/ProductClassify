from django.db.models import Q

from classes.constants import ParamIds
from parametr.models import Parametr
from agregat.models import Agregat


class AgregatSelector:
    @staticmethod
    def search_by_name(query: str):
        return Parametr.objects.filter(
           Q(parametr_type__exact=ParamIds.AGREGAT) &
           Q(name__icontains=query)
        )

    @staticmethod
    def fetch_all():
        return Parametr.objects.filter(
            Q(parametr_type__exact=ParamIds.AGREGAT)
        )

    @staticmethod
    def fetch_by_id(pk: int):
        return Parametr.objects.get(pk=pk)

    @staticmethod
    def agregat_params_list(agregat_id: int):
        return (
            Agregat.objects
            .filter(agr=agregat_id)
            .select_related("par")
            .order_by("num")
        )

    @staticmethod
    def fetch_agregat_parametr(agregat_id: int, param_id: int):
        return (
            Agregat.objects.filter(agr=agregat_id, par=param_id)
            .select_related("agr", "par")
            .first()
        )