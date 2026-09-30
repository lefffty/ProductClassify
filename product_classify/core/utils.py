from django.db import transaction
from django.db.models import Model


def change_num(obj1: Model, obj2: Model, max_value: int):
    with transaction.atomic():
        old_num_1 = obj1.num
        old_num_2 = obj2.num

        temp_num_1 = max_value
        temp_num_2 = max_value - 1
        obj1.num = temp_num_1
        obj2.num = temp_num_2
        obj1.save(update_fields=["num"])
        obj2.save(update_fields=["num"])

        obj1.num = old_num_2
        obj2.num = old_num_1
        obj1.save(update_fields=["num"])
        obj2.save(update_fields=["num"])
