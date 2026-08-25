from django.urls import reverse

from tests.end2end.ei.list.base import EiListBaseEndToEndTest
from tests.end2end.pages.ei.list import EiListPage

from ei.models import Ei


class EiListNavigationEndToEndTest(EiListBaseEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.list_page = EiListPage(self.page)

    def test_add_btn_redirects_to_create_page(self):
        create_page = self.list_page.add()
        create_url = reverse("ei:add")
        full_url = self.server_url + create_url
        create_page.check_url_is_correct(full_url)

    def test_detail_btn_redirects_to_detail_page(self):
        ei = Ei.objects.first()
        index = ei.pk
        detail_page = self.list_page.detail(index)
        detail_url = reverse("ei:detail", args=[index])
        full_url  = self.server_url + detail_url
        detail_page.check_url_is_correct(full_url)

    def test_edit_btn_redirects_to_edit_page(self):
        ei = Ei.objects.first()
        index = ei.pk
        edit_page = self.list_page.edit(index)
        edit_url = reverse("ei:edit", args=[index])
        full_url  = self.server_url + edit_url
        edit_page.check_url_is_correct(full_url)

    def test_delete_btn_redirects_to_delete_page(self):
        ei = Ei.objects.first()
        index = ei.pk
        delete_page = self.list_page.delete(index)
        delete_url = reverse("ei:delete", args=[index])
        full_url  = self.server_url + delete_url
        delete_page.check_url_is_correct(full_url)
