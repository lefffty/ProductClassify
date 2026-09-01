from playwright.sync_api import Page, expect

from tests.end2end.components.pages.base import BasePage


class EnumClassCreatePage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.enum_class_form_container = page.locator("#enum-class-form-container")
        self.enum_class_form_card = page.locator("#enum-class-form-card")
        self.enum_class_form_header = page.locator("#enum-class-form-header")

        self.enum_class_form = page.locator("#enum-class-form")

        self.enum_class_submit_btn = page.locator("#enum-class-submit-btn")
        self.enum_class_cancel_btn = page.locator("#enum-class-cancel-btn")

        self.enum_class_delete_alert = page.locator("#enum-class-delete-alert")
        self.enum_class_delete_warning = page.locator("#enum-class-delete-warning")
        self.enum_class_delete_hint = page.locator("#enum-class-delete-hint")
        self.enum_class_delete_info = page.locator("#enum-class-delete-info")
        self.enum_class_delete_id = page.locator("#enum-class-delete-id")
        self.enum_class_delete_name = page.locator("#enum-class-delete-name")
        self.enum_class_delete_parent = page.locator("#enum-class-delete-parent")

        self.non_field_errors = page.locator("#enum-class-form-non-field-errors")

        self.fields = {
            (name, field_type): page.locator(f"#id_{name}")
            for name, field_type in [
                ("name", "input"), 
                ("short_name", "input"), 
                ("main_class", "select"),
            ]
        }

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)

    def check_form_container_is_visible(self):
        expect(self.enum_class_form_container).to_be_visible()

    def check_form_card_is_visible(self):
        expect(self.enum_class_form_card).to_be_visible()

    def check_form_header_is_visible(self):
        expect(self.enum_class_form_header).to_be_visible()

    def check_form_header_text_is_correct(self, text: str):
        expect(self.enum_class_form_header).to_have_text(text)

    def check_form_is_visible(self):
        expect(self.enum_class_form).to_be_visible()

    def check_submit_btn_is_visible(self):
        expect(self.enum_class_submit_btn).to_be_visible()

    def check_cancel_btn_is_visible(self):
        expect(self.enum_class_submit_btn).to_be_visible()

    def check_submit_btn_text_is_correct(self, text: str):
        expect(self.enum_class_submit_btn).to_have_text(text)

    def check_cancel_btn_text_is_correct(self, text: str):
        expect(self.enum_class_cancel_btn).to_have_text(text)

    def check_form_fields_are_visible(self):
        for field in self.fields.values():
            expect(field).to_be_visible()

    def cancel(self):
        from tests.end2end.components.pages.classes.index import IndexPage
        self.enum_class_cancel_btn.click(force=True)
        return IndexPage(self._page)

    def submit(self, data: dict):
        from tests.end2end.components.pages.classes.index import IndexPage
        for (field_name, field_type), field in self.fields.items():
            if field_type == 'input':
                field.fill(data[field_name])
            elif field_type == 'select':
                field.select_option(index=data[field_name])
        self.enum_class_submit_btn.click(force=True)
        return IndexPage(self._page)
