from playwright.sync_api import Page, expect

from tests.end2end.pages.base import BasePage

from tests.end2end.pages.ei.delete import EiDeletePage
from tests.end2end.pages.ei.edit import EiEditPage


class EiDetailPage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.ei_detail_title = page.locator("#ei-detail-title")
        self.ei_detail_id_badge = page.locator("#ei-detail-id-badge")
        self.ei_detail_short_badge = page.locator("#ei-detail-short-badge")
        self.ei_detail_info_header = page.locator("#ei-detail-info-header")
        self.ei_detail_name_value = page.locator("#ei-detail-name-value")
        self.ei_detail_short_value = page.locator("#ei-detail-short-value")
        self.ei_detail_code_value = page.locator("#ei-detail-code-value")
        self.ei_detail_factor_value = page.locator("#ei-detail-factor-value")
        self.ei_detail_parent_value = page.locator("#ei-detail-parent-value")
        self.ei_detail_parent_id = page.locator("#ei-detail-parent-id")
        self.ei_detail_parent_none = page.locator("#ei-detail-parent-none")

        self.ei_detail_edit_btn = page.locator("#ei-detail-edit-btn")
        self.ei_detail_delete_btn = page.locator("#ei-detail-delete-btn")
        self.ei_detail_parent_btn = page.locator("#ei-detail-parent-link")
        self.ei_detail_back_btn = page.locator("#ei-detail-back-btn")

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)

    def check_ei_title_is_visible(self):
        expect(self.ei_detail_title).to_be_visible()

    def check_ei_id_badge_is_visible(self):
        expect(self.ei_detail_id_badge).to_be_visible()

    def check_ei_short_badge_is_visible(self):
        expect(self.ei_detail_short_badge).to_be_visible()

    def check_ei_info_header_is_visible(self):
        expect(self.ei_detail_info_header).to_be_visible()

    def check_ei_name_value_is_visible(self):
        expect(self.ei_detail_name_value).to_be_visible()

    def check_ei_short_value_is_visible(self):
        expect(self.ei_detail_short_value).to_be_visible()

    def check_ei_code_value_is_visible(self):
        expect(self.ei_detail_code_value).to_be_visible()

    def check_ei_factor_value_is_visible(self):
        expect(self.ei_detail_factor_value).to_be_visible()

    def check_ei_parent_value_is_visible(self):
        expect(self.ei_detail_parent_value).to_be_visible()

    def check_ei_parent_id_is_visible(self):
        expect(self.ei_detail_parent_id).to_be_visible()

    def check_ei_parent_none_is_visible(self):
        expect(self.ei_detail_parent_none).to_be_visible()

    def check_edit_btn_is_visible(self):
        expect(self.ei_detail_edit_btn).to_be_visible()

    def check_delete_bth_is_visible(self):
        expect(self.ei_detail_delete_btn).to_be_visible()

    def check_parent_btn_is_visible(self):
        expect(self.ei_detail_parent_id).to_be_visible()

    def check_back_btn_is_visible(self):
        expect(self.ei_detail_back_btn).to_be_visible()

    def check_ei_detail_title_text_is_correct(self, text: str):
        expect(self.ei_detail_title).to_have_text(text)

    def check_ei_detail_id_badge_text_is_correct(self, text: str):
        expect(self.ei_detail_id_badge).to_have_text(text)

    def check_ei_detail_short_badge_text_is_correct(self, text: str):
        expect(self.ei_detail_short_badge).to_have_text(text)

    def check_ei_detail_info_header_text_is_correct(self, text: str):
        expect(self.ei_detail_info_header).to_have_text(text)

    def check_ei_detail_name_value_text_is_correct(self, text: str):
        expect(self.ei_detail_name_value).to_have_text(text)

    def check_ei_detail_short_value_text_is_correct(self, text: str):
        expect(self.ei_detail_short_value).to_have_text(text)

    def check_ei_detail_code_value_text_is_correct(self, text: str):
        expect(self.ei_detail_code_value).to_have_text(text)

    def check_ei_detail_factor_value_text_is_correct(self, text: str):
        expect(self.ei_detail_factor_value).to_have_text(text)

    def check_ei_detail_parent_value_text_is_correct(self, text: str):
        expect(self.ei_detail_parent_value).to_have_text(text)

    def check_ei_detail_parent_id_text_is_correct(self, text: str):
        expect(self.ei_detail_parent_id).to_have_text(text)

    def check_ei_detail_parent_none_text_is_correct(self, text: str):
        expect(self.ei_detail_parent_none).to_have_text(text)

    def check_edit_btn_text_is_correct(self, text: str):
        expect(self.ei_detail_edit_btn).to_have_text(text)

    def check_delete_bth_text_is_correct(self, text: str):
        expect(self.ei_detail_delete_btn).to_have_text(text)

    def check_parent_btn_text_is_correct(self, text: str):
        expect(self.ei_detail_parent_btn).to_have_text(text)

    def check_back_btn_text_is_correct(self, text: str):
        expect(self.ei_detail_back_btn).to_have_text(text)

    def edit(self):
        self.ei_detail_edit_btn.click(force=True)
        return EiEditPage(self._page)

    def delete(self):
        self.ei_detail_delete_btn.click(force=True)
        return EiDeletePage(self._page)

    def back(self):
        from tests.end2end.pages.ei.list import EiListPage
        self.ei_detail_back_btn.click(force=True)
        return EiListPage(self._page)

    def go_to_parent(self):
        self.ei_detail_parent_btn.click(force=True)
        return EiDetailPage(self._page)
