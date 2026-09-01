from django.urls import reverse

from tests.end2end.classes.index.base import IndexPageBaseEndToEndTest
from tests.end2end.components.pages.classes.index import IndexPage


class IndexPageNavigationEndToEndTest(IndexPageBaseEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.index_page = IndexPage(self.page)

    def test_classes_btn_redirects_to_add_product_class_page(self):
        add_prod_class_url = reverse("classes:add_prod_class")
        full_url = self.server_url + add_prod_class_url
        add_prod_class_page = self.index_page.add_prod_class()
        add_prod_class_page.check_url_is_correct(full_url)

    def test_enums_btn_redirects_to_add_enum_class_page(self):
        add_enum_class_url = reverse("classes:add_enum_class")
        full_url = self.server_url + add_enum_class_url
        add_enum_class_page = self.index_page.add_enum_class()
        add_enum_class_page.check_url_is_correct(full_url)

    def test_ei_btn_redirects_to_add_ei_page(self):
        add_ei_url = reverse("ei:add")
        full_url = self.server_url + add_ei_url
        add_ei_page = self.index_page.add_ei()
        add_ei_page.check_url_is_correct(full_url)

    def test_params_btn_redirects_to_add_parameter_page(self):
        add_parameter_url = reverse("parametr:add")
        full_url = self.server_url + add_parameter_url
        add_parameter_page = self.index_page.add_parameter()
        add_parameter_page.check_url_is_correct(full_url)

    def test_enum_values_btn_redirects_to_add_enum_page(self):
        add_enum_url = reverse("enums:add")
        full_url = self.server_url + add_enum_url
        add_enum_page = self.index_page.add_enum()
        add_enum_page.check_url_is_correct(full_url)

    def test_products_btn_redirects_to_add_product_page(self):
        add_product_url = reverse("products:add")
        full_url = self.server_url + add_product_url
        add_product_page = self.index_page.add_product()
        add_product_page.check_url_is_correct(full_url)
