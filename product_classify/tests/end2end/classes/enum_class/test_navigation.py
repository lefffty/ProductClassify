from django.urls import reverse

from tests.end2end.classes.enum_class.base import EnumClassCreateEndToEndTest
from tests.end2end.components.pages.classes.enums.create import EnumClassCreatePage

from classes.constants import EnumsIds


class EnumClassNavigationEndToEndTest(EnumClassCreateEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.create_page = EnumClassCreatePage(self.page)

    def test_cancel_btn_redirects_to_index_page(self):
        index_url = reverse("classes:index")
        full_url = self.server_url + index_url
        index_page = self.create_page.cancel()
        index_page.check_url_is_correct(full_url)

    def test_submit_btn_redirects_to_index_page(self):
        index_url = reverse("classes:index")
        full_url = self.server_url + index_url
        data = {
            "name": "test name",
            "short_name": "test",
            "main_class": 1
        }
        index_page = self.create_page.submit(data)
        index_page.check_url_is_correct(full_url)
