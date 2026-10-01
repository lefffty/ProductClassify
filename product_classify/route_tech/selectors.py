from django.db import connection

from typing import List
from collections import namedtuple

from core.queries import EASQueries, TechRouteQueries

from route_tech.models import GroupWorkingCenter, EconomicActivitySubject, ProdOperation

EASRecordResult = namedtuple(
    "EASRecordResult",
    field_names=[
        "id",
        "name",
        "short_name",
        "level",
    ]
)

TechRouteRecord = namedtuple(
    "TechRouteRecord",
    field_names=[
        "input_prod_name",
        "input_prod_short_name",
        "output_prod_name",
        "output_prod_short_name",
        "operation_name",
        "operation_short_name",
        "profession_name",
        "gwc_name",
        "gwc_short_name",
        "eas_name",
        "eas_short_name",
        "qualification_name",
        "input_quantity",
        "output_quantity",
        "t_pz",
        "t_sht",
        "num_of_workers",
    ]
)


class EASSelector:
    @staticmethod
    def get_all_eas_descendants(eas_id: int) -> List[EASRecordResult]:
        with connection.cursor() as cursor:
            cursor.execute(EASQueries.GET_ALL_EAS_DESCENDANTS, [eas_id])
            children = cursor.fetchall()
        return [EASRecordResult(*child) for child in children]

    @staticmethod
    def fetch_list():
        return (
            EconomicActivitySubject.objects
            .select_related(
                "main_class",
                "main_subject",
            )
        )


class GWCSelector:
    @staticmethod
    def fetch_list():
        return (
            GroupWorkingCenter.objects
            .select_related(
                "main_class",
                "eas",
            )
        )


class ProdOperationSelector:
    @staticmethod
    def fetch_list():
        return (
            ProdOperation.objects
            .select_related(
                "prod",
                "tech_oper",
                "profession",
                "center",
                "qualification",
            )
        )


class TechRouteSelector:
    @staticmethod
    def get_tech_route(prod_id: int) -> List[TechRouteRecord]:
        with connection.cursor() as cursor:
            cursor.execute(TechRouteQueries.GET_TECH_ROUTE, [prod_id])
            data = cursor.fetchall()
        return [TechRouteRecord(*record) for record in data]
