from django.db import connection

from typing import List

from core.queries import EASQueries, TechRouteQueries
from core.types import EASRecordResult, TechRouteRecord

from route_tech.models import GroupWorkingCenter, EconomicActivitySubject, ProdOperation


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
