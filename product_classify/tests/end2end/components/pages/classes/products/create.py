from playwright.sync_api import Page, expect

from tests.end2end.components.pages.base import BasePage


class ProdClassCreatePage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.prod_class_form_container = page.locator("#prod-class-form-container")
        self.prod_class_form_card = page.locator("#prod-class-form-card")
        self.prod_class_form_header = page.locator("#prod-class-form-header")

        self.prod_class_form = page.locator("#prod-class-form")

        self.prod_class_submit_btn = page.locator("#prod-class-submit-btn")
        self.prod_class_cancel_btn = page.locator("#prod-class-cancel-btn")

        self.prod_class_delete_alert = page.locator("#prod-class-delete-alert")
        self.prod_class_delete_warning = page.locator("#prod-class-delete-warning")
        self.prod_class_delete_hint = page.locator("#prod-class-delete-hint")
        self.prod_class_delete_info = page.locator("#prod-class-delete-info")
        self.prod_class_delete_name = page.locator("#prod-class-delete-name")
        self.prod_class_delete_short = page.locator("#prod-class-delete-short")
        self.prod_class_delete_ei = page.locator("#prod-class-delete-ei")

        self.fields = {
            (name, field_type): page.locator(f"#id_{name}")
            for name, field_type in [
                ("name", "input"),
                ("short_name", "input"),
                ("base_ei", "select"),
                ("main_class", "select")
            ]
        }

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)

    def check_container_is_visible(self):
        expect(self.prod_class_form_container).to_be_visible()

    def check_card_is_visible(self):
        expect(self.prod_class_form_card).to_be_visible()

    def check_header_is_visible(self):
        expect(self.prod_class_form_header).to_be_visible()

    def check_form_is_visible(self):
        expect(self.prod_class_form).to_be_visible()

    def check_submit_btn_is_visible(self):
        expect(self.prod_class_submit_btn).to_be_visible()

    def check_cancel_btn_is_visible(self):
        expect(self.prod_class_cancel_btn).to_be_visible()

    def check_form_fields_are_visible(self):
        for field in self.fields.values():
            expect(field).to_be_visible()

    def check_header_text_is_correct(self, text: str):
        expect(self.prod_class_form_header).to_have_text(text)

    def check_submit_btn_text_is_correct(self, text: str):
        expect(self.prod_class_submit_btn).to_have_text(text)

    def check_cancel_btn_text_is_correct(self, text: str):
        expect(self.prod_class_cancel_btn).to_have_text(text)

    def cancel(self):
        from tests.end2end.components.pages.classes.index import IndexPage
        self.prod_class_cancel_btn.click(force=True)
        return IndexPage(self._page)

    def submit(self, data: dict):
        from tests.end2end.components.pages.classes.index import IndexPage
        for (name, field_type), field in self.fields.items():
            if field_type == "input":
                field.fill(data[name])
            elif field_type == "select":
                field.select_option(index=data[name])
        self.prod_class_submit_btn.click(force=True)
        return IndexPage(self._page)
