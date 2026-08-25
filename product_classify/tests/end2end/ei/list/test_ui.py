from django.urls import reverse

from tests.end2end.ei.base import EiBaseEndToEndTest

from ei.models import Ei


class EiListUIEndToEndTest(EiBaseEndToEndTest):
    def test_url_is_correct(self):
        list_url = reverse("ei:list")
        full_url = self.server_url + list_url
        self.list_page.check_url_is_correct(full_url)

    def test_page_title_is_visible(self):
        self.list_page.check_page_title_is_visible()

    def test_add_btn_is_visible(self):
        self.list_page.check_add_btn_is_visible()

    def test_list_counter_is_visible(self):
        self.list_page.check_list_counter_is_visible()

    def test_table_header_is_visible(self):
        self.list_page.check_table_header_is_visible()

    def test_table_body_is_visible(self):
        self.list_page.check_table_body_is_visible()

    def test_title_text_is_correct(self):
        text = "Единицы измерения"
        self.list_page.check_page_title_text_is_correct(text)

    def test_add_btn_text_is_correct(self):
        text = "Добавить единицу измерения"
        self.list_page.check_add_btn_text_is_correct(text)

    def test_list_counter_text_is_correct(self):
        text = str(Ei.objects.count())
        self.list_page.check_list_counter_text_is_correct(text)

    def test_table_header_columns_names_are_correct(self):
        names = [
            "ID",
            "Название",
            "Сокращение",
            "Код",
        ]
        self.list_page.check_table_header_columns_names_are_correct(names)

    def test_table_body_nth_element_data_is_correct(self):
        ei = Ei.objects.first()
        data = {
            "id": str(ei.pk),
            "name": ei.name,
            "short_name": ei.short_name,
            "code": ei.code,
        }
        self.list_page.check_table_body_nth_element_data_is_correct(ei.pk, data)

    def test_table_body_nth_element_actions_data_is_correct(self):
        ei = Ei.objects.first()
        index = ei.pk
        names = [
            "Подробнее",
            "Редактировать",
            "Удалить",
        ]
        self.list_page.check_table_body_nth_element_actions_data_is_correct(index, names)


class EiEmptyListUIEndToEndTest(EiBaseEndToEndTest):
    fixtures = None

    def test_url_is_correct(self):
        list_url = reverse("ei:list")
        full_url = self.server_url + list_url
        self.list_page.check_url_is_correct(full_url)

    def test_empty_ei_list_message_is_visible(self):
        self.list_page.check_empty_list_message_is_visible()

    def test_empty_ei_list_message_text_is_correct(self):
        text = "Единицы измерения отсутствуют"
        self.list_page.check_empty_list_message_text_is_correct(text)

    def test_add_first_btn_is_visible(self):
        self.list_page.check_add_first_btn_is_visible()

    def test_add_first_btn_text_is_correct(self):
        text = "Добавить первую единицу"
        self.list_page.check_add_first_btn_text_is_correct(text)
