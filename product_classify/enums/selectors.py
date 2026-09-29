from enums.models import Enums


class EnumSelector:
    @staticmethod
    def fetch_enums_list(class_id: int):
        return (
            Enums.objects
            .filter(enum__main_class__id=class_id)
            .select_related("enum", "enum__main_class")
            .order_by("id")
        )

    @staticmethod
    def fetch_detail_information():
        return (
            Enums.objects
            .select_related(
                "enum",
                "enum__main_class",
            )
        )
