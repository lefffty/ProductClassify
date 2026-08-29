from django.urls import reverse

from tests.end2end.components.pages.ei.list import EiListPage
from tests.end2end.base import EndToEndTest


class EiListBaseEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = cls.server_url + reverse("ei:list")
        cls.page.goto(cls.url)

        cls.list_page = EiListPage(cls.page)
