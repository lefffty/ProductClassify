from django.db import connection

from collections import namedtuple

from core.queries import ProdQueries


ModificationResult = namedtuple("ModificationResult", field_names=["modification_id"])


class ProdService:
    @staticmethod
    def create_modification(
        product_id: int, **kwargs
    ) -> ModificationResult:
        name = kwargs.get("name")
        short_name = kwargs.get("short_name")
        with connection.cursor() as cursor:
            params = [product_id, name, short_name]
            cursor.execute(ProdQueries.CREATE_MODIFICATION, params=params)
            row = cursor.fetchall()[0]
        return ModificationResult(*row)
