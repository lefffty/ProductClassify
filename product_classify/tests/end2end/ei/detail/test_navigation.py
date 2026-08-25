from django.urls import reverse

from tests.end2end.ei.detail.base import (
    EiParentDetailBaseEndToEndTest,
    EiChildDetailBaseEndToEndTest
)


class EiParentNavigationEndToEndTest(EiParentDetailBaseEndToEndTest):
    def tearDown(self):
        from tests.end2end.pages.ei.detail import EiDetailPage
        self.page.goto(self.url)
        self.detail_page = EiDetailPage(self.page)

    def test_edit_btn_redirects_to_edit_page(self):
        edit_page = self.detail_page.edit()
        edit_url = reverse("ei:edit", args=[self.ei_id])
        full_url = self.server_url + edit_url
        edit_page.check_url_is_correct(full_url)

    def test_delete_btn_redirects_to_delete_page(self):
        delete_page = self.detail_page.delete()
        delete_url = reverse("ei:delete", args=[self.ei_id])
        full_url = self.server_url + delete_url
        delete_page.check_url_is_correct(full_url)

    def test_back_btn_redirects_to_list_page(self):
        list_page = self.detail_page.back()
        list_url = reverse("ei:list")
        full_url = self.server_url + list_url
        list_page.check_url_is_correct(full_url)


class EiChildNavigationEndToEndTest(EiChildDetailBaseEndToEndTest):
    def tearDown(self):
        from tests.end2end.pages.ei.detail import EiDetailPage
        self.page.goto(self.url)
        self.detail_page = EiDetailPage(self.page)

    def test_parent_btn_redirects_to_detail_page(self):
        detail_page = self.detail_page.go_to_parent()
        detail_url = reverse("ei:detail", args=[self.ei.main_class.pk])
        full_url = self.server_url + detail_url
        detail_page.check_url_is_correct(full_url)
