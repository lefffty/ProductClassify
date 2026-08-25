from playwright.sync_api import Page, expect

from tests.end2end.pages.base import BasePage
from tests.end2end.pages.ei.create import EiCreatePage
from tests.end2end.pages.ei.delete import EiDeletePage
from tests.end2end.pages.ei.detail import EiDetailPage
from tests.end2end.pages.ei.edit import EiEditPage


class EiListPage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.page_title = page.locator("#ei-page-title")
        self.add_btn = page.locator("#ei-add-btn")
        self.ei_counter = page.locator("#ei-count")
        self.table_header = page.locator("#ei-table-header")
        self.table_body = page.locator("#ei-table-body")
        self.empty_list_msg = page.locator("#ei-empty-list-msg")
        self.add_first_btn = page.locator("#ei-add-first-btn")

        self.ei_selector = "#ei-row-{}"
        self.ei_edit_id = "#ei-edit-{}"
        self.ei_detail_id = "#ei-detail-{}"
        self.ei_delete_id = "#ei-delete-{}"

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)

    def check_page_title_is_visible(self):
        expect(self.page_title).to_be_visible(timeout=self.timeout)

    def check_add_btn_is_visible(self):
        expect(self.add_btn).to_be_visible(timeout=self.timeout)

    def check_list_counter_is_visible(self):
        expect(self.ei_counter).to_be_visible(timeout=self.timeout)

    def check_table_header_is_visible(self):
        expect(self.table_header).to_be_visible(timeout=self.timeout)

    def check_table_body_is_visible(self):
        expect(self.table_body).to_be_visible(timeout=self.timeout)

    def check_empty_list_message_is_visible(self):
        expect(self.empty_list_msg).to_be_visible()

    def check_add_first_btn_is_visible(self):
        expect(self.add_first_btn).to_be_visible()

    def check_page_title_text_is_correct(self, text: str):
        expect(self.page_title).to_have_text(text, timeout=self.timeout)

    def check_add_btn_text_is_correct(self, text: str):
        expect(self.add_btn).to_have_text(text, timeout=self.timeout)

    def check_list_counter_text_is_correct(self, text: str):
        expect(self.ei_counter).to_have_text(text, timeout=self.timeout)

    def check_table_header_columns_names_are_correct(self, names: list[str]):
        headers = self.table_header.locator("tr th")
        for header, name in zip(headers.all(), names):
            expect(header).to_have_text(name, timeout=self.timeout)

    def check_table_body_nth_element_data_is_correct(
        self,
        index: int,
        data: dict,
    ):
        entry = self.table_body.locator(self.ei_selector.format(index)).locator("td")
        for i, value in enumerate(data.values()):
            expect(entry.nth(i)).to_have_text(value, timeout=self.timeout)

    def check_table_body_nth_element_actions_data_is_correct(
        self,
        index: int,
        names: list[str],
    ):
        row = self.table_body.locator(self.ei_selector.format(index))
        actions = row.locator("td").last.locator("div a")
        for i, name in enumerate(names):
            expect(actions.nth(i)).to_have_text(name, timeout=self.timeout)

    def check_empty_list_message_text_is_correct(self, text: str):
        expect(self.empty_list_msg).to_have_text(text)

    def check_add_first_btn_text_is_correct(self, text: str):
        expect(self.add_first_btn).to_have_text(text)

    def add(self):
        self.add_btn.click(force=True)
        return EiCreatePage(self._page)

    def edit(self, index: int):
        edit_btn = self._page.locator(self.ei_edit_id.format(index))
        edit_btn.click(force=True)
        return EiEditPage(self._page)

    def detail(self, index: int):
        detail_btn = self._page.locator(self.ei_detail_id.format(index))
        detail_btn.click(force=True)
        return EiDetailPage(self._page)

    def delete(self, index: int):
        delete_btn = self._page.locator(self.ei_delete_id.format(index))
        delete_btn.click(force=True)
        return EiDeletePage(self._page)
