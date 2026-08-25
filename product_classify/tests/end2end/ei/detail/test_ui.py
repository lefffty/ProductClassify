from django.urls import reverse

from tests.end2end.ei.detail.base import (
    EiParentDetailBaseEndToEndTest,
    EiChildDetailBaseEndToEndTest
)


class EiParentDetailUIEndToEndTest(EiParentDetailBaseEndToEndTest):
    def test_url_is_correct(self):
        detail_url = reverse("ei:detail", args=[self.ei_id])
        full_url = self.server_url + detail_url
        self.detail_page.check_url_is_correct(full_url)

    def test_ei_title_is_visible(self):
        self.detail_page.check_ei_title_is_visible()

    def test_ei_id_badge_is_visible(self):
        self.detail_page.check_ei_id_badge_is_visible()

    def test_ei_short_badge_is_visible(self):
        self.detail_page.check_ei_short_badge_is_visible()

    def test_ei_name_value_is_visible(self):
        self.detail_page.check_ei_name_value_is_visible()

    def test_ei_short_value_is_visible(self):
        self.detail_page.check_ei_short_value_is_visible()

    def test_ei_code_value_is_visible(self):
        self.detail_page.check_ei_code_value_is_visible()

    def test_ei_parent_none_is_visible(self):
        self.detail_page.check_ei_parent_none_is_visible()

    def test_edit_btn_is_visible(self):
        self.detail_page.check_edit_btn_is_visible()

    def test_delete_btn_is_visible(self):
        self.detail_page.check_delete_bth_is_visible()

    def test_back_btn_is_visible(self):
        self.detail_page.check_back_btn_is_visible()

    def test_ei_detail_title_text_is_correct(self):
        text = self.ei.name
        self.detail_page.check_ei_detail_title_text_is_correct(text)

    def test_ei_detail_id_badge_text_is_correct(self):
        text = f"ID: {self.ei.pk}"
        self.detail_page.check_ei_detail_id_badge_text_is_correct(text)

    def test_ei_detail_short_badge_text_is_correct(self):
        text = self.ei.short_name
        self.detail_page.check_ei_detail_short_badge_text_is_correct(text)

    def test_ei_detail_info_badge_text_is_correct(self):
        text = "Детальная информация"
        self.detail_page.check_ei_detail_info_header_text_is_correct(text)

    def test_ei_detail_name_value_text_is_correct(self):
        text = self.ei.name
        self.detail_page.check_ei_detail_name_value_text_is_correct(text)

    def test_ei_detail_short_value_text_is_correct(self):
        text = self.ei.short_name
        self.detail_page.check_ei_detail_short_value_text_is_correct(text)

    def test_ei_detail_code_value_text_is_correct(self):
        text = self.ei.code
        self.detail_page.check_ei_detail_code_value_text_is_correct(text)

    def test_ei_detail_factor_value_text_is_correct(self):
        text = "1,0"
        self.detail_page.check_ei_detail_factor_value_text_is_correct(text)

    def test_ei_detail_parent_none_text_is_correct(self):
        text = "—"
        self.detail_page.check_ei_detail_parent_none_text_is_correct(text)

    def test_edit_btn_text_is_correct(self):
        text = "Редактировать"
        self.detail_page.check_edit_btn_text_is_correct(text)

    def test_delete_btn_text_is_correct(self):
        text = "Удалить"
        self.detail_page.check_delete_bth_text_is_correct(text)

    def test_back_btn_text_is_correct(self):
        text = "Вернуться к списку"
        self.detail_page.check_back_btn_text_is_correct(text)


class EiChildDetailIUEndToEndTest(EiChildDetailBaseEndToEndTest):
    def test_ei_detail_parent_id_is_visible(self):
        self.detail_page.check_ei_parent_id_is_visible()

    def test_parent_btn_is_visible(self):
        self.detail_page.check_parent_btn_is_visible()

    def test_ei_detail_parent_id_text_is_correct(self):
        text = f"(ID: {self.ei.main_class.pk})"
        self.detail_page.check_ei_detail_parent_id_text_is_correct(text)

    def test_parent_btn_text_is_visible(self):
        text = f"{self.ei.main_class.name}"
        self.detail_page.check_parent_btn_text_is_correct(text)
