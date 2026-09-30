from django.db import connection

from typing import List
from collections import namedtuple

from core.queries import ProdComponentQueries, SpecificationLogsQueries


TotalCostRatioResult = namedtuple(
    "TotalCostRatioResult",
    field_names=[
        "parent_id",
        "parent_prod_name",
        "child_id",
        "child_prod_name",
        "quantity",
        "ei_short_name",
        "total_cost",
        "level",
    ],
)
SpecificationRecordResult = namedtuple(
    "SpecificationRecordResult",
    field_names=[
        "pair_id",
        "parent_id",
        "child_id",
        "prod_num",
        "quantity",
    ],
)

SpecificationLogResult = namedtuple(
    "SpecificationLogResult",
    field_names=[
        "log_id",
        "parent_id",
        "comp_id",
        "updated_at",
        "log_string",
    ],
)


class ProdComponentSelector:
    @staticmethod
    def is_parent_prod(
        product_id: int
    ) -> int:
        with connection.cursor() as cursor:
            cursor.execute(ProdComponentQueries.IS_PARENT_PROD, params=[product_id])
            is_parent = cursor.fetchone()[0]
        return is_parent

    @staticmethod
    def total_cost_ratio(
        product_id: int, quantity: int, convert_factor: float
    ) -> List[TotalCostRatioResult]:
        with connection.cursor() as cursor:
            cursor.execute(
                ProdComponentQueries.TOTAL_COST_RATIO_NEW, params=[
                    product_id,
                    quantity, 
                    convert_factor
                ]
            )
            rows = cursor.fetchall()
        return [TotalCostRatioResult(*row) for row in rows]

    @staticmethod
    def product_specification(product_id: int) -> List[SpecificationRecordResult]:
        with connection.cursor() as cursor:
            cursor.execute(
                ProdComponentQueries.PRODUCT_SPECIFICATION, params=[product_id]
            )
            rows = cursor.fetchall()
        return [SpecificationRecordResult(*row) for row in rows]


class SpecificationLogsSelector:
    @staticmethod
    def get_changelog(product_id: int) -> List[SpecificationLogResult]:
        with connection.cursor() as cursor:
            cursor.execute(SpecificationLogsQueries.GET_CHANGE_LOG, params=[product_id])
            rows = cursor.fetchall()
        return [SpecificationLogResult(*row) for row in rows]
