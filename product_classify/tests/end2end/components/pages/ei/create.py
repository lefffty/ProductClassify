from playwright.sync_api import Page, expect

from tests.end2end.components.pages.base import BasePage


class EiCreatePage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.form_container = page.locator("#ei-form-container")
        self.form_card = page.locator("#ei-form-card")
        self.form_header = page.locator("#ei-form-header")
        self.form = page.locator("#ei-form")

        self.field_help_texts = {
            field: page.locator(f"label[for='id_{field}']") for field in ["name", "short_name", "code", "convert_factor", "main_class"]
        }
        self.fields = {
            field: page.locator(f"{field_type}[id='id_{field}']") for field_type, field in [
                ("input", "name"), 
                ("input", "short_name"), 
                ("input", "code"), 
                ("input", "convert_factor"),
                ("select", "main_class")
            ]
        }

        self.submit_btn = page.locator("#ei-form-submit-btn")
        self.cancel_btn = page.locator("#ei-form-cancel-btn")

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)

    def check_ei_container_is_visible(self):
        expect(self.form_container).to_be_visible()

    def check_ei_form_card_is_visible(self):
        expect(self.form_card).to_be_visible()

    def check_ei_form_header_is_visible(self):
        expect(self.form_header).to_be_visible()

    def check_ei_form_is_visible(self):
        expect(self.form).to_be_visible()

    def check_submit_btn_is_visible(self):
        expect(self.submit_btn).to_be_visible()

    def check_cancel_btn_is_visible(self):
        expect(self.cancel_btn).to_be_visible()

    def check_form_header_text_is_correct(self, text: str):
        expect(self.form_header).to_have_text(text)

    def check_form_submit_btn_text_is_correct(self, text: str):
        expect(self.submit_btn).to_have_text(text)

    def check_form_cancel_btn_text_is_correct(self, text: str):
        expect(self.cancel_btn).to_have_text(text)

    def check_form_fields_are_visible(self):
        for field in self.fields.values():
            expect(field).to_be_visible()

    def check_form_fields_help_texts_are_visible(self):
        for help_field in self.field_help_texts.values():
            expect(help_field).to_be_visible()

    def check_form_fields_help_texts_are_correct(self, help_texts: list[str]):
        for help_field, help_text in zip(self.field_help_texts.values(), help_texts):
            expect(help_field).to_have_text(help_text)
