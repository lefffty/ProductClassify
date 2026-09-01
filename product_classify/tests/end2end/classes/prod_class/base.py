from django.urls import reverse

from tests.end2end.components.pages.classes.products.create import ProdClassCreatePage
from tests.end2end.base import EndToEndTest


class ProdClassCreateEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = cls.server_url + reverse("classes:add_prod_class")
        cls.page.goto(cls.url)

        cls.create_page = ProdClassCreatePage(cls.page)

