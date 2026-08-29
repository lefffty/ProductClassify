from django.urls import reverse

from tests.end2end.ei.delete.base import EiDeleteBaseEndToEndTest
from tests.end2end.components.pages.ei.delete import EiDeletePage

from ei.models import Ei


class EiDeleteNavigationEndToEndTest(EiDeleteBaseEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.delete_page = EiDeletePage(self.page)

    def test_cancel_btn_redirects_to_list_page(self):
        list_page = self.delete_page.cancel()
        list_url = reverse("ei:list")
        full_url = self.server_url + list_url
        list_page.check_url_is_correct(full_url)

    def test_submit_btn_redirects_to_list_page_and_decreases_rows_count(self):
        before_count = Ei.objects.count()
        list_page = self.delete_page.submit()
        list_url = reverse("ei:list")
        full_url = self.server_url + list_url
        list_page.check_url_is_correct(full_url)
        list_page.check_rows_count(before_count - 1)
