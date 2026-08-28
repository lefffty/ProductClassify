from django.urls import reverse

from faker import Faker

from tests.end2end.ei.edit.base import EiEditEndToEndTest
from tests.end2end.components.pages.ei.edit import EiEditPage

from ei.constants import EiConsts


class EiEditNavigationEndToEndTest(EiEditEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.create_page = EiEditPage(self.page)

    def test_cancel_btn_redirects_to_list_page(self):
        list_page = self.edit_page.cancel()
        list_url = reverse("ei:list")
        full_url = self.server_url + list_url
        list_page.check_url_is_correct(full_url)

    def test_submit_btn_redirects_to_list_page(self):
        faker = Faker()
        data = {
            "name": faker.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": faker.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            "code": faker.name()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": "3.14",
            "main_class": "3"
        }
        detail_url = reverse("ei:detail", args=[self.ei_pk])
        full_url = self.server_url + detail_url
        detail_page = self.edit_page.submit(data)
        detail_page.check_url_is_correct(full_url)
