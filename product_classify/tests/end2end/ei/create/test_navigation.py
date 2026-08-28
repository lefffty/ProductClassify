from django.urls import reverse

from faker import Faker

from tests.end2end.ei.create.base import EiCreateBaseEndToEndTest
from tests.end2end.components.pages.ei.create import EiCreatePage

from ei.constants import EiConsts


class EiCreateNavigationEndToEndTest(EiCreateBaseEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.create_page = EiCreatePage(self.page)

    def test_cancel_btn_redirects_to_list_page(self):
        list_page = self.create_page.cancel()
        create_url = reverse("ei:list")
        full_url = self.server_url + create_url
        list_page.check_url_is_correct(full_url)

    def test_submit_btn_redirect_to_detail_page(self):
        faker = Faker()
        data = {
            "name": faker.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": faker.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            "code": faker.name()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": "3.14",
            "main_class": "3"
        }
        list_page = self.create_page.submit(data)
        list_url = reverse("ei:list")
        full_url = self.server_url + list_url
        list_page.check_url_is_correct(full_url)
