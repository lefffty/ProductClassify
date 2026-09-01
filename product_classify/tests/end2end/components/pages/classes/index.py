from playwright.sync_api import Page, expect

from tests.end2end.components.pages.base import BasePage
from tests.end2end.components.pages.ei.create import EiCreatePage
from tests.end2end.components.pages.products.create import ProductCreatePage
from tests.end2end.components.pages.parametr.create import ParametrCreatePage
from tests.end2end.components.pages.enums.create import EnumCreatePage
from tests.end2end.components.pages.classes.enums.create import EnumClassCreatePage
from tests.end2end.components.pages.classes.products.create import ProdClassCreatePage


class IndexPage(BasePage):
    def __init__(self, page: Page):
        self._page = page

        self.home_title = page.locator("#home-title")
        self.home_subtitle = page.locator("#home-subtitle")

        self.home_card_classes_title = page.locator("#home-card-classes-title")
        self.home_card_classes_text = page.locator("#home-card-classes-text")
        self.home_card_classes_btn = page.locator("#home-card-classes-btn")

        self.home_card_enums_title = page.locator("#home-card-enums-title")
        self.home_card_enums_text = page.locator("#home-card-enums-text")
        self.home_card_enums_btn = page.locator("#home-card-enums-btn")

        self.home_card_ei_title = page.locator("#home-card-ei-title")
        self.home_card_ei_text = page.locator("#home-card-ei-text")
        self.home_card_ei_btn = page.locator("#home-card-ei-btn")

        self.home_card_params_title = page.locator("#home-card-params-title")
        self.home_card_params_text = page.locator("#home-card-params-text")
        self.home_card_params_btn = page.locator("#home-card-params-btn")

        self.home_card_enum_values_title = page.locator("#home-card-enum-values-title")
        self.home_card_enum_values_text = page.locator("#home-card-enum-values-text")
        self.home_card_enum_values_btn = page.locator("#home-card-enum-values-btn")

        self.home_card_products_title = page.locator("#home-card-products-title")
        self.home_card_products_text = page.locator("#home-card-products-text")
        self.home_card_products_btn = page.locator("#home-card-products-btn")

    def check_url_is_correct(self, url):
        expect(self._page).to_have_url(url)

    def check_home_title_is_visible(self):
        expect(self.home_title).to_be_visible()

    def check_home_title_text_is_correct(self, text: str):
        expect(self.home_title).to_have_text(text)

    def check_home_subtitle_is_visible(self):
        expect(self.home_subtitle).to_be_visible()

    def check_home_subtitle_text_is_correct(self, text: str):
        expect(self.home_subtitle).to_have_text(text)

    def check_classes_title_is_visible(self):
        expect(self.home_card_classes_title).to_be_visible()

    def check_classes_text_is_visible(self):
        expect(self.home_card_classes_text).to_be_visible()

    def check_classes_btn_is_visible(self):
        expect(self.home_card_classes_btn).to_be_visible()

    def check_classes_title_text_is_correct(self, text: str):
        expect(self.home_card_classes_title).to_have_text(text)

    def check_classes_text_text_is_correct(self, text: str):
        expect(self.home_card_classes_text).to_have_text(text)

    def check_classes_btn_text_is_correct(self, text: str):
        expect(self.home_card_classes_btn).to_have_text(text)

    def check_enums_title_is_visible(self):
        expect(self.home_card_enums_title).to_be_visible()

    def check_enums_text_is_visible(self):
        expect(self.home_card_enums_text).to_be_visible()

    def check_enums_btn_is_visible(self):
        expect(self.home_card_enums_btn).to_be_visible()

    def check_enums_title_text_is_correct(self, text: str):
        expect(self.home_card_enums_title).to_have_text(text)

    def check_enums_text_text_is_correct(self, text: str):
        expect(self.home_card_enums_text).to_have_text(text)

    def check_enums_btn_text_is_correct(self, text: str):
        expect(self.home_card_enums_btn).to_have_text(text)

    def check_ei_title_is_visible(self):
        expect(self.home_card_ei_title).to_be_visible()

    def check_ei_text_is_visible(self):
        expect(self.home_card_ei_text).to_be_visible()

    def check_ei_btn_is_visible(self):
        expect(self.home_card_ei_btn).to_be_visible()

    def check_ei_title_text_is_correct(self, text: str):
        expect(self.home_card_ei_title).to_have_text(text)

    def check_ei_text_text_is_correct(self, text: str):
        expect(self.home_card_ei_text).to_have_text(text)

    def check_ei_btn_text_is_correct(self, text: str):
        expect(self.home_card_ei_btn).to_have_text(text)

    def check_params_title_is_visible(self):
        expect(self.home_card_params_title).to_be_visible()

    def check_params_text_is_visible(self):
        expect(self.home_card_params_text).to_be_visible()

    def check_params_btn_is_visible(self):
        expect(self.home_card_params_btn).to_be_visible()

    def check_params_title_text_is_correct(self, text: str):
        expect(self.home_card_params_title).to_have_text(text)

    def check_params_text_text_is_correct(self, text: str):
        expect(self.home_card_params_text).to_have_text(text)

    def check_params_btn_text_is_correct(self, text: str):
        expect(self.home_card_params_btn).to_have_text(text)

    def check_enum_values_title_is_visible(self):
        expect(self.home_card_enum_values_title).to_be_visible()

    def check_enum_values_text_is_visible(self):
        expect(self.home_card_enum_values_text).to_be_visible()

    def check_enum_values_btn_is_visible(self):
        expect(self.home_card_enum_values_btn).to_be_visible()

    def check_enum_values_title_text_is_correct(self, text: str):
        expect(self.home_card_enum_values_title).to_have_text(text)

    def check_enum_values_text_text_is_correct(self, text: str):
        expect(self.home_card_enum_values_text).to_have_text(text)

    def check_enum_values_btn_text_is_correct(self, text: str):
        expect(self.home_card_enum_values_btn).to_have_text(text)

    def check_products_title_is_visible(self):
        expect(self.home_card_products_title).to_be_visible()

    def check_products_text_is_visible(self):
        expect(self.home_card_products_text).to_be_visible()

    def check_products_btn_is_visible(self):
        expect(self.home_card_products_btn).to_be_visible()

    def check_products_title_text_is_correct(self, text: str):
        expect(self.home_card_products_title).to_have_text(text)

    def check_products_text_text_is_correct(self, text: str):
        expect(self.home_card_products_text).to_have_text(text)

    def check_products_btn_text_is_correct(self, text: str):
        expect(self.home_card_products_btn).to_have_text(text)

    def add_prod_class(self):
        self.home_card_classes_btn.click(force=True)
        return ProdClassCreatePage(self._page)

    def add_enum_class(self):
        self.home_card_enums_btn.click(force=True)
        return EnumClassCreatePage(self._page)

    def add_ei(self):
        self.home_card_ei_btn.click(force=True)
        return EiCreatePage(self._page)

    def add_parameter(self):
        self.home_card_params_btn.click(force=True)
        return ParametrCreatePage(self._page)

    def add_enum(self):
        self.home_card_enum_values_btn.click(force=True)
        return EnumCreatePage(self._page)

    def add_product(self):
        self.home_card_products_btn.click(force=True)
        return ProductCreatePage(self._page)
