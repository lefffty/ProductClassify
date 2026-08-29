from tests.end2end.ei.delete.base import EiDeleteBaseEndToEndTest


class EiDeleteUIEndToEndTest(EiDeleteBaseEndToEndTest):
    def test_url_is_correct(self):
        self.delete_page.check_url_is_correct(self.url)

    def test_form_header_is_visible(self):
        self.delete_page.check_form_header_is_visible()

    def test_form_is_visible(self):
        self.delete_page.check_form_is_visible()

    def test_alert_is_visible(self):
        self.delete_page.check_alert_is_visible()

    def test_warning_is_visible(self):
        self.delete_page.check_warning_is_visible()

    def test_hint_is_visible(self):
        self.delete_page.check_hint_is_visible()

    def test_info_is_visible(self):
        self.delete_page.check_info_is_visible()

    def test_help_texts_are_visible(self):
        self.delete_page.check_help_texts_are_visible()

    def test_fields_are_visible(self):
        self.delete_page.check_fields_are_visible()

    def test_submit_btn_is_visible(self):
        self.delete_page.check_submit_btn_is_visible()

    def test_cancel_btn_is_visible(self):
        self.delete_page.check_cancel_btn_is_visible()

    def test_form_header_text_is_correct(self):
        text = "Удаление единицы измерения"
        self.delete_page.check_form_header_text_is_correct(text)

    def test_warning_text_is_correct(self):
        text = "Вы действительно хотите удалить эту единицу измерения?"
        self.delete_page.check_warning_text_is_correct(text)

    def test_hint_text_is_correct(self):
        text = "Это действие необратимо."
        self.delete_page.check_hint_text_is_correct(text)

    def test_help_texts_are_correct(self):
        texts = [
            "ID",
            "Название",
            "Сокращение",
            "Код",
            "Множитель",
            "Родительская единица",
        ]
        self.delete_page.check_help_texts_are_correct(texts)

    def test_fields_texts_are_correct(self):
        texts = [
            str(self.ei.pk),
            self.ei.name,
            self.ei.short_name,
            self.ei.code,
            str(self.ei.convert_factor).replace(".", ","),
            str(self.ei.main_class) if self.ei.main_class else '—'
        ]
        self.delete_page.check_fields_texts_are_correct(texts)

    def test_cancel_btn_text_is_correct(self):
        text = "Отмена"
        self.delete_page.check_cancel_btn_text_is_correct(text)

    def test_submit_btn_text_is_correct(self):
        text = "Удалить"
        self.delete_page.check_submit_btn_text_is_correct(text)
