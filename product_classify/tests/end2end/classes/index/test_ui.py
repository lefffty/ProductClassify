from tests.end2end.classes.index.base import IndexPageBaseEndToEndTest


class IndexPageUIEndToEndTest(IndexPageBaseEndToEndTest):
    def test_title_element(self):
        self.index_page.check_home_title_is_visible()
        text = "Добро пожаловать"
        self.index_page.check_home_title_text_is_correct(text)

    def test_subtitle_element(self):
        self.index_page.check_home_subtitle_is_visible()
        text = "Управление справочной системой"
        self.index_page.check_home_subtitle_text_is_correct(text)

    def test_home_card_classes_elements(self):
        self.index_page.check_classes_title_is_visible()
        self.index_page.check_classes_text_is_visible()
        self.index_page.check_classes_btn_is_visible()

        title = "Классы изделий"
        text = "Управление классификацией изделий"
        btn = "Добавить класс"

        self.index_page.check_classes_title_text_is_correct(title)
        self.index_page.check_classes_text_text_is_correct(text)
        self.index_page.check_classes_btn_text_is_correct(btn)

    def test_home_card_enums_elements(self):
        self.index_page.check_enums_title_is_visible()
        self.index_page.check_enums_text_is_visible()
        self.index_page.check_enums_btn_is_visible()

        title = "Классы перечислений"
        text = "Управление перечисляемыми типами"
        btn = "Добавить класс"

        self.index_page.check_enums_title_text_is_correct(title)
        self.index_page.check_enums_text_text_is_correct(text)
        self.index_page.check_enums_btn_text_is_correct(btn)

    def test_home_card_ei_elements(self):
        self.index_page.check_ei_title_is_visible()
        self.index_page.check_ei_text_is_visible()
        self.index_page.check_ei_btn_is_visible()

        title = "Единицы измерения"
        text = "Справочник единиц измерения"
        btn = "Добавить единицу"

        self.index_page.check_ei_title_text_is_correct(title)
        self.index_page.check_ei_text_text_is_correct(text)
        self.index_page.check_ei_btn_text_is_correct(btn)

    def test_home_card_params_elements(self):
        self.index_page.check_params_title_is_visible()
        self.index_page.check_params_text_is_visible()
        self.index_page.check_params_btn_is_visible()

        title = "Параметры"
        text = "Управление параметрами изделий"
        btn = "Добавить параметр"

        self.index_page.check_params_title_text_is_correct(title)
        self.index_page.check_params_text_text_is_correct(text)
        self.index_page.check_params_btn_text_is_correct(btn)

    def test_home_card_enum_values_elements(self):
        self.index_page.check_enum_values_title_is_visible()
        self.index_page.check_enum_values_text_is_visible()
        self.index_page.check_enum_values_btn_is_visible()

        title = "Значения перечислений"
        text = "Добавление значений в перечисления"
        btn = "Добавить значение"

        self.index_page.check_enum_values_title_text_is_correct(title)
        self.index_page.check_enum_values_text_text_is_correct(text)
        self.index_page.check_enum_values_btn_text_is_correct(btn)

    def test_home_card_products_elements(self):
        self.index_page.check_products_title_is_visible()
        self.index_page.check_products_text_is_visible()
        self.index_page.check_products_btn_is_visible()

        title = "Изделия"
        text = "Управление каталогом изделий"
        btn = "Добавить изделие"

        self.index_page.check_products_title_text_is_correct(title)
        self.index_page.check_products_text_text_is_correct(text)
        self.index_page.check_products_btn_text_is_correct(btn)
