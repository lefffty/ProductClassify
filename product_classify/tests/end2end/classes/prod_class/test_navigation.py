from django.urls import reverse

from tests.end2end.classes.prod_class.base import ProdClassCreateEndToEndTest
from tests.end2end.components.pages.classes.products.create import ProdClassCreatePage


class ProdClassCreateNavigationEndToEndTest(ProdClassCreateEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.create_page = ProdClassCreatePage(self.page)

    def test_cancel_btn_redirects_to_index_page(self):
        index_page_url = reverse("classes:index")
        full_url = self.server_url + index_page_url
        index_page = self.create_page.cancel()
        index_page.check_url_is_correct(full_url)

    def test_submit_btn_redirects_to_index_page(self):
        index_page_url = reverse("classes:index")
        full_url = self.server_url + index_page_url
        data = {
            "name": "test name",
            "short_name": "short",
            "base_ei": 1,
            "main_class": 3,
        }
        index_page = self.create_page.submit(data)
        index_page.check_url_is_correct(full_url)
