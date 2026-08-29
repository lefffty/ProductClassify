from classes.models import ClassStruct

from tests.end2end.classes.list.base import (
    ClassesEmptyListBaseEndToEndTest,
    ClassesFilledListBaseEndToEndTest
)


class ClassesEmptyListUIEndToEndTest(ClassesEmptyListBaseEndToEndTest):
    def test_url_is_correct(self):
        self.list_page.check_url_is_correct(self.url)

    def test_container_is_visible(self):
        self.list_page.check_container_is_visible()

    def test_main_card_is_visible(self):
        self.list_page.check_main_card_is_visible()

    def test_main_title_is_visible(self):
        self.list_page.check_main_title_is_visible()

    def test_main_class_name_is_visible(self):
        self.list_page.check_main_class_name_is_visible()

    def test_main_info_is_visible(self):
        self.list_page.check_main_info_is_visible()

    def test_main_id_is_visible(self):
        self.list_page.check_main_id_is_visible()

    def test_main_fullname_is_visible(self):
        self.list_page.check_main_fullname_is_visible()

    def test_main_short_is_visible(self):
        self.list_page.check_main_short_is_visible()

    def test_main_ei_is_visible(self):
        self.list_page.check_main_ei_is_visible()

    def test_list_card_is_visible(self):
        self.list_page.check_list_card_is_visible()

    def test_list_header_is_visible(self):
        self.list_page.check_list_header_is_visible()

    def test_list_title_is_visible(self):
        self.list_page.check_list_title_is_visible()

    def test_list_count_is_visible(self):
        self.list_page.check_list_count_is_visible()

    def test_list_body_is_visible(self):
        self.list_page.check_list_body_is_visible()

    def test_actions_card_is_visible(self):
        self.list_page.check_actions_card_is_visible()

    def test_actions_body_is_visible(self):
        self.list_page.check_actions_body_is_visible()

    def test_delete_main_btn_is_visible(self):
        self.list_page.check_delete_main_btn_is_visible()

    def test_edit_main_btn_is_visible(self):
        self.list_page.check_edit_main_btn_is_visible()

    def test_add_param_btn_is_visible(self):
        self.list_page.check_add_param_btn_is_visible()

    def test_params_list_btn_is_visible(self):
        self.list_page.check_params_list_btn_is_visible()

    def test_main_title_text_is_correct(self):
        text = f"Подклассы класса {self.prod_class.name}"
        self.list_page.check_main_title_text_is_correct(text)

    def test_main_class_name_text_is_correct(self):
        text = self.prod_class.name
        self.list_page.check_main_class_name_text_is_correct(text)

    def test_main_id_text_is_correct(self):
        text = str(self.prod_class.pk)
        self.list_page.check_main_id_text_is_correct(text)

    def test_main_fullname_text_is_correct(self):
        text = self.prod_class.name
        self.list_page.check_main_fullname_text_is_correct(text)

    def test_short_text_is_correct(self):
        text = "—"
        self.list_page.check_main_short_text_is_correct(text)

    def test_main_ei_text_is_correct(self):
        text = "Не задана"
        self.list_page.check_main_ei_text_is_correct(text)

    def test_list_title_text_is_correct(self):
        text = "Список подклассов"
        self.list_page.check_list_title_text_is_correct(text)

    def test_empty_state_is_visible(self):
        self.list_page.check_empty_state_is_visible()

    def test_empty_msg_is_visible(self):
        self.list_page.check_empty_msg_is_visible()

    def test_empty_msg_text_is_correct(self):
        text = "Подклассы отсутствуют"
        self.list_page.check_empty_msg_text_is_correct(text)

    def test_list_count_text_is_correct(self):
        text = str(ClassStruct.objects.filter(main_class__exact=self.prod_class.pk).count())
        self.list_page.check_list_count_text_is_correct(text)

    def test_delete_main_btn_text_is_visible(self):
        text = "Удалить класс"
        self.list_page.check_delete_main_btn_text_is_correct(text)

    def test_edit_main_btn_text_is_correct(self):
        text = "Редактировать"
        self.list_page.check_edit_main_btn_text_is_correct(text)

    def test_add_param_btn_text_is_correct(self):
        text = "Добавить параметр"
        self.list_page.check_add_param_btn_text_is_correct(text)

    def test_params_list_btn_text_is_correct(self):
        text = "Параметры класса"
        self.list_page.check_params_list_btn_text_is_correct(text)


class ClassesFilledListUIEndToEndTest(ClassesFilledListBaseEndToEndTest):
    def test_table_is_visible(self):
        self.list_page.check_table_is_visible()

    def test_table_header_is_visible(self):
        self.list_page.check_table_header_is_visible()

    def test_table_body_is_visible(self):
        self.list_page.check_table_body_is_visible()

    def test_list_count_text_is_correct(self):
        text = str(ClassStruct.objects.filter(main_class__exact=self.prod_class.pk).count())
        self.list_page.check_list_count_text_is_correct(text)

    def test_row_data_is_correct(self):
        class_id = self.child_prod_class1.pk
        self.list_page.check_row_is_visible(class_id)

        self.list_page.check_row_id_text_is_correct(class_id, str(self.child_prod_class1.pk))
        self.list_page.check_row_name_text_is_correct(class_id, self.child_prod_class1.name)
        self.list_page.check_row_short_text_is_correct(class_id, self.child_prod_class1.short_name)
        self.list_page.check_row_ei_text_is_correct(class_id, "—")

        self.list_page.check_row_products_btn_text_is_correct(class_id, "Список изделий")
        self.list_page.check_row_edit_btn_text_is_correct(class_id, "Редактировать")
        self.list_page.check_row_delete_btn_text_is_correct(class_id, "Удалить")
        self.list_page.check_row_params_btn_text_is_correct(class_id, "Параметры класса")

