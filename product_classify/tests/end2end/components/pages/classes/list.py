from playwright.sync_api import Page, expect


from tests.end2end.components.pages.base import BasePage


class ClassesListPage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.category_container = page.locator("#category-container")

        self.category_main_card = page.locator("#category-main-card")
        self.category_main_title = page.locator("#category-main-title")
        self.category_main_class_name = page.locator("#category-main-class-name")
        self.category_main_info = page.locator("#category-main-info")
        self.category_main_id = page.locator("#category-main-id")
        self.category_main_fullname = page.locator("#category-main-fullname")
        self.category_main_short = page.locator("#category-main-short")
        self.category_main_ei = page.locator("#category-main-ei")

        self.category_list_card = page.locator("#category-list-card")
        self.category_list_header = page.locator("#category-list-header")
        self.category_list_title = page.locator("#category-list-title")
        self.category_list_count = page.locator("#category-list-count")
        self.category_list_body = page.locator("#category-list-body")

        self.category_table = page.locator("#category-table")
        self.category_table_header = page.locator("#category-table-header")
        self.category_table_body = page.locator("#category-table-body")

        self.category_empty_state = page.locator("#category-empty-state")
        self.category_empty_msg = page.locator("#category-empty-msg")

        self.category_actions_card = page.locator("#category-actions-card")
        self.category_actions_body = page.locator("#category-actions-body")
        self.category_delete_main_btn = page.locator("#category-delete-main-btn")
        self.category_edit_main_btn = page.locator("#category-edit-main-btn")
        self.category_add_param_btn = page.locator("#category-add-param-btn")
        self.category_params_list_btn = page.locator("#category-params-list-btn")

    def get_row(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}")

    def get_row_id_cell(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-id")

    def get_row_name_cell(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-name")

    def get_row_short_cell(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-short")

    def get_row_ei_cell(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-ei")

    def get_row_actions(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-actions")

    def get_row_products_btn(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-products-btn")

    def get_row_edit_btn(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-edit-btn")

    def get_row_delete_btn(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-delete-btn")

    def get_row_params_btn(self, class_id: int):
        return self._page.locator(f"#category-row-{class_id}-params-btn")

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)

    def check_container_is_visible(self):
        expect(self.category_container).to_be_visible()

    def check_main_card_is_visible(self):
        expect(self.category_main_card).to_be_visible()

    def check_main_title_is_visible(self):
        expect(self.category_main_title).to_be_visible()

    def check_main_class_name_is_visible(self):
        expect(self.category_main_class_name).to_be_visible()

    def check_main_info_is_visible(self):
        expect(self.category_main_info).to_be_visible()

    def check_main_id_is_visible(self):
        expect(self.category_main_id).to_be_visible()

    def check_main_fullname_is_visible(self):
        expect(self.category_main_fullname).to_be_visible()

    def check_main_short_is_visible(self):
        expect(self.category_main_short).to_be_visible()

    def check_main_ei_is_visible(self):
        expect(self.category_main_ei).to_be_visible()

    def check_list_card_is_visible(self):
        expect(self.category_list_card).to_be_visible()

    def check_list_header_is_visible(self):
        expect(self.category_list_header).to_be_visible()

    def check_list_title_is_visible(self):
        expect(self.category_list_title).to_be_visible()

    def check_list_count_is_visible(self):
        expect(self.category_list_count).to_be_visible()

    def check_list_body_is_visible(self):
        expect(self.category_list_body).to_be_visible()

    def check_table_is_visible(self):
        expect(self.category_table).to_be_visible()

    def check_table_header_is_visible(self):
        expect(self.category_table_header).to_be_visible()

    def check_table_body_is_visible(self):
        expect(self.category_table_body).to_be_visible()

    def check_empty_state_is_visible(self):
        expect(self.category_empty_state).to_be_visible()

    def check_empty_msg_is_visible(self):
        expect(self.category_empty_msg).to_be_visible()

    def check_actions_card_is_visible(self):
        expect(self.category_actions_card).to_be_visible()

    def check_actions_body_is_visible(self):
        expect(self.category_actions_body).to_be_visible()

    def check_delete_main_btn_is_visible(self):
        expect(self.category_delete_main_btn).to_be_visible()

    def check_edit_main_btn_is_visible(self):
        expect(self.category_edit_main_btn).to_be_visible()

    def check_add_param_btn_is_visible(self):
        expect(self.category_add_param_btn).to_be_visible()

    def check_params_list_btn_is_visible(self):
        expect(self.category_params_list_btn).to_be_visible()

    def check_main_title_text_is_correct(self, text: str):
        expect(self.category_main_title).to_have_text(text)

    def check_main_class_name_text_is_correct(self, text: str):
        expect(self.category_main_class_name).to_have_text(text)

    def check_main_id_text_is_correct(self, text: str):
        expect(self.category_main_id).to_have_text(text)

    def check_main_fullname_text_is_correct(self, text: str):
        expect(self.category_main_fullname).to_have_text(text)

    def check_main_short_text_is_correct(self, text: str):
        expect(self.category_main_short).to_have_text(text)

    def check_main_ei_text_is_correct(self, text: str):
        expect(self.category_main_ei).to_have_text(text)

    def check_list_title_text_is_correct(self, text: str):
        expect(self.category_list_title).to_have_text(text)

    def check_list_count_text_is_correct(self, text: str):
        expect(self.category_list_count).to_have_text(text)

    def check_empty_msg_text_is_correct(self, text: str):
        expect(self.category_empty_msg).to_have_text(text)

    def check_delete_main_btn_text_is_correct(self, text: str):
        expect(self.category_delete_main_btn).to_have_text(text)

    def check_edit_main_btn_text_is_correct(self, text: str):
        expect(self.category_edit_main_btn).to_have_text(text)

    def check_add_param_btn_text_is_correct(self, text: str):
        expect(self.category_add_param_btn).to_have_text(text)

    def check_params_list_btn_text_is_correct(self, text: str):
        expect(self.category_params_list_btn).to_have_text(text)

    def check_row_is_visible(self, class_id: int):
        expect(self.get_row(class_id)).to_be_visible()

    def check_row_id_text_is_correct(self, class_id: int, text: str):
        expect(self.get_row_id_cell(class_id)).to_have_text(text)

    def check_row_name_text_is_correct(self, class_id: int, text: str):
        expect(self.get_row_name_cell(class_id)).to_have_text(text)

    def check_row_short_text_is_correct(self, class_id: int, text: str):
        expect(self.get_row_short_cell(class_id)).to_have_text(text)

    def check_row_ei_text_is_correct(self, class_id: int, text: str):
        expect(self.get_row_ei_cell(class_id)).to_have_text(text)

    def check_row_products_btn_text_is_correct(self, class_id: int, text: str):
        expect(self.get_row_products_btn(class_id)).to_have_text(text)

    def check_row_edit_btn_text_is_correct(self, class_id: int, text: str):
        expect(self.get_row_edit_btn(class_id)).to_have_text(text)

    def check_row_delete_btn_text_is_correct(self, class_id: int, text: str):
        expect(self.get_row_delete_btn(class_id)).to_have_text(text)

    def check_row_params_btn_text_is_correct(self, class_id: int, text: str):
        expect(self.get_row_params_btn(class_id)).to_have_text(text)
