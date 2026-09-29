from ei.models import Ei


class EiSelector:
    @staticmethod
    def select_all_order_by_id():
        return Ei.objects.order_by("id")

    @staticmethod
    def search_by_name(query: str):
        return Ei.objects.filter(name__icontains=query).order_by("id")
