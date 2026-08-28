from django.urls import reverse

from tests.end2end.base import EndToEndTest
from tests.end2end.components.pages.ei.create import EiCreatePage


class EiCreateBaseEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = cls.server_url + reverse("ei:add")
        cls.page.goto(cls.url)

        cls.create_page = EiCreatePage(cls.page)
