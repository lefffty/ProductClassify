from tests.end2end.ei.create.base import EiCreateBaseEndToEndTest


class EiCreateEndToEndTest(EiCreateBaseEndToEndTest):
    def test_url_is_correct(self):
        self.create_page.check_url_is_correct(self.url)

    def test_ei_container_is_visible(self):
        self.create_page.check_ei_container_is_visible()

    def test_ei_form_card_is_visible(self):
        self.create_page.check_ei_form_card_is_visible()

    def test_ei_form_header_is_visible(self):
        self.create_page.check_ei_form_header_is_visible()

    def test_ei_form_is_visible(self):
        self.create_page.check_ei_form_is_visible()

    def test_submit_btn_is_visible(self):
        self.create_page.check_submit_btn_is_visible()

    def test_cancel_btn_is_visible(self):
        self.create_page.check_cancel_btn_is_visible()

    def test_form_fields_are_visible(self):
        self.create_page.check_form_fields_are_visible()

    def test_form_fields_help_texts_are_visible(self):
        self.create_page.check_form_fields_help_texts_are_visible()

    def test_form_header_text_is_correct(self):
        text = "Добавление единицы измерения"
        self.create_page.check_form_header_text_is_correct(text)

    def test_form_submit_btn_text_is_correct(self):
        text = "Добавить"
        self.create_page.check_form_submit_btn_text_is_correct(text)

    def test_form_cancel_btn_text_is_correct(self):
        text = "Отмена"
        self.create_page.check_form_cancel_btn_text_is_correct(text)

    def test_form_fields_help_text_are_correct(self):
        help_texts: list[str] = [
            "Название единицы измерения",
            "Сокращенное название единицы измерения",
            "Код единицы измерения",
            "Множитель для перевода",
            "Родительская единица измерения",
        ]
        self.create_page.check_form_fields_help_texts_are_correct(help_texts)
