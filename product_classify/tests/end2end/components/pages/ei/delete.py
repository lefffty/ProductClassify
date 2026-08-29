from playwright.sync_api import Page, expect

from tests.end2end.components.pages.base import BasePage


class EiDeletePage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.form_header = page.locator("#ei-form-header")
        self.form = page.locator("#ei-form")

        self.alert = page.locator("#ei-delete-alert")
        self.warning = page.locator("#ei-delete-warning")
        self.hint = page.locator("#ei-delete-hint")
        self.info = page.locator("#ei-delete-info")

        fields = (
            "id",
            "name",
            "short",
            "code",
            "factor",
            "main_class"
        )

        self.help_texts = {
            field: page.locator(f"#ei-delete-{field}-help")
            for field in fields
        }
        self.fields = {
            field: page.locator(f"#ei-delete-{field}")
            for field in fields
        }

        self.submit_btn = page.locator("#ei-form-submit-btn")
        self.cancel_btn = page.locator("#ei-form-cancel-btn")

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)

    def check_form_header_is_visible(self):
        expect(self.form_header).to_be_visible()

    def check_form_is_visible(self):
        expect(self.form).to_be_visible()

    def check_alert_is_visible(self):
        expect(self.alert).to_be_visible()

    def check_warning_is_visible(self):
        expect(self.warning).to_be_visible()

    def check_hint_is_visible(self):
        expect(self.hint).to_be_visible()

    def check_info_is_visible(self):
        expect(self.info).to_be_visible()

    def check_help_texts_are_visible(self):
        for _, help_field in self.help_texts.items():
            expect(help_field).to_be_visible()

    def check_fields_are_visible(self):
        for _, field in self.fields.items():
            expect(field).to_be_visible()

    def check_submit_btn_is_visible(self):
        expect(self.submit_btn).to_be_visible()

    def check_cancel_btn_is_visible(self):
        expect(self.cancel_btn).to_be_visible()

    def check_form_header_text_is_correct(self, text: str):
        expect(self.form_header).to_have_text(text)

    def check_warning_text_is_correct(self, text: str):
        expect(self.warning).to_have_text(text)

    def check_hint_text_is_correct(self, text: str):
        expect(self.hint).to_have_text(text)

    def check_help_texts_are_correct(self, texts: list[str]):
        for field, text in zip(self.help_texts.values(), texts):
            expect(field).to_have_text(text)

    def check_fields_texts_are_correct(self, texts: list[str]):
        for (_, field), text in zip(self.fields.items(), texts):
            expect(field).to_have_text(text)

    def check_cancel_btn_text_is_correct(self, text: str):
        expect(self.cancel_btn).to_have_text(text)

    def check_submit_btn_text_is_correct(self, text: str):
        expect(self.submit_btn).to_have_text(text)

    def cancel(self):
        from tests.end2end.components.pages.ei.list import EiListPage
        self.cancel_btn.click(force=True)
        return EiListPage(self._page)

    def submit(self):
        from tests.end2end.components.pages.ei.list import EiListPage
        self.submit_btn.click(force=True)
        return EiListPage(self._page)
