from django.urls import reverse

from tests.end2end.classes.enum_class.base import EnumClassCreateEndToEndTest


class EnumClassCreateUIEndToEndTest(EnumClassCreateEndToEndTest):
    def test_url_is_correct(self):
        add_enum_class_url = reverse("classes:add_enum_class")
        full_url = self.server_url + add_enum_class_url
        self.create_page.check_url_is_correct(full_url)

    def test_form_container_is_visible(self):
        self.create_page.check_form_container_is_visible()

    def test_form_card_is_visible(self):
        self.create_page.check_form_card_is_visible()

    def test_form_header_is_visible(self):
        self.create_page.check_form_header_is_visible()

    def test_form_is_visible(self):
        self.create_page.check_form_is_visible()

    def test_submit_btn_is_visible(self):
        self.create_page.check_submit_btn_is_visible()

    def test_cancel_btn_is_visible(self):
        self.create_page.check_submit_btn_is_visible()

    def text_form_fields_are_visible(self):
        self.create_page.check_form_fields_are_visible()

    def test_form_header_text_is_correct(self):
        text = "Добавление класса перечисления"
        self.create_page.check_form_header_text_is_correct(text)

    def test_submit_btn_text_is_correct(self):
        text = "Добавить"
        self.create_page.check_submit_btn_text_is_correct(text)

    def test_cancel_btn_text_is_correct(self):
        text = "Отмена"
        self.create_page.check_cancel_btn_text_is_correct(text)
