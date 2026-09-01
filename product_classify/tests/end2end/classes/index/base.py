from django.urls import reverse

from tests.end2end.components.pages.classes.index import IndexPage
from tests.end2end.base import EndToEndTest


class IndexPageBaseEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = cls.server_url + reverse("classes:index")
        cls.page.goto(cls.url)

        cls.index_page = IndexPage(cls.page)
