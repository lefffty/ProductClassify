from django.db import connection

from typing import List
from collections import namedtuple

from core.queries import EASQueries

EASRecordResult = namedtuple(
    "EASRecordResult",
    field_names=[
        "id",
        "name",
        "short_name",
        "level",
    ]
)


class EASSelector:
    @staticmethod
    def get_all_eas_descendants(eas_id: int) -> List[EASRecordResult]:
        with connection.cursor() as cursor:
            cursor.execute(EASQueries.GET_ALL_EAS_DESCENDANTS, [eas_id])
            children = cursor.fetchall()
        return [EASRecordResult(*child) for child in children]
