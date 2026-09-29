from classes.constants import ParamIds

from parametr.models import Parametr


class ParametrSelector:
    @staticmethod
    def fetch_parametrs_list():
        return (
            Parametr.objects
            .exclude(parametr_type__exact=ParamIds.AGREGAT)
            .select_related("parametr_type")
            .only(
                "id",
                "name",
                "short_name",
                "parametr_type__name",
            )
            .order_by("id")
        )

    @staticmethod
    def search_by_name(query: str):
        return (
            Parametr.objects
            .exclude(parametr_type__exact=ParamIds.AGREGAT)
            .select_related("parametr_type")
            .order_by("id")
            .filter(name__icontains=query)
            .only(
                "id",
                "name",
                "short_name",
                "parametr_type__name",
            )
        )

    @staticmethod
    def parameters():
        return (
            Parametr.objects.
            exclude(parametr_type__exact=ParamIds.AGREGAT)
            .select_related("par_ei")
            .order_by("id")
        )

    @staticmethod
    def agregats():
        return (
            Parametr.objects
            .filter(parametr_type__exact=ParamIds.AGREGAT)
        )
