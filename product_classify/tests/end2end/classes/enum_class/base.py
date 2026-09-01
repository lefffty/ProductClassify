from django.urls import reverse

from tests.end2end.components.pages.classes.enums.create import EnumClassCreatePage
from tests.end2end.base import EndToEndTest


class EnumClassCreateEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = cls.server_url + reverse("classes:add_enum_class")
        cls.page.goto(cls.url)

        cls.create_page = EnumClassCreatePage(cls.page)

