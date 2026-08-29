from django.urls import reverse
from django.test import override_settings

from tests.end2end.classes.list.base import (
    ClassesEmptyListBaseEndToEndTest,
    ClassesFilledListBaseEndToEndTest
)
from tests.end2end.components.pages.classes.list import ClassesListPage


class ClassesEmptyListNavigationEndToEndTest(ClassesEmptyListBaseEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.list_page = ClassesListPage(self.page)

    def test_delete_btn_redirects_to_delete_page(self):
        delete_page = self.list_page.delete()
        delete_url = reverse("classes:delete", args=[self.prod_class.pk])
        full_url = self.server_url + delete_url
        delete_page.check_url_is_correct(full_url)

    def test_edit_btn_redirects_to_edit_page(self):
        edit_page = self.list_page.edit()
        edit_url = reverse("classes:edit", args=[self.prod_class.pk])
        full_url = self.server_url + edit_url
        edit_page.check_url_is_correct(full_url)

    def test_add_param_btn_redirects_to_add_param_page(self):
        add_param_page = self.list_page.add_param()
        add_param_url = reverse("classes:add_param", args=[self.prod_class.pk])
        full_url = self.server_url + add_param_url
        add_param_page.check_url_is_correct(full_url)

    def test_params_list_btn_redirects_to_params_list_page(self):
        params_list_page = self.list_page.params_list()
        params_list_url = reverse("classes:params_list", args=[self.prod_class.pk])
        full_url = self.server_url + params_list_url
        params_list_page.check_url_is_correct(full_url)


@override_settings(DEBUG=True)
class ClassesFilledListNavigationEndToEndTest(ClassesFilledListBaseEndToEndTest):
    def tearDown(self):
        self.page.goto(self.url)
        self.list_page = ClassesListPage(self.page)

    def test_edit_subclass_btn_redirects_to_edit_page(self):
        class_id = self.child_prod_class1.pk
        edit_page = self.list_page.edit_subclass(class_id)
        edit_url = reverse("classes:edit", args=[class_id])
        full_url = self.server_url + edit_url
        edit_page.check_url_is_correct(full_url)

    def test_params_list_subclass_btn_redirects_to_params_list_page(self):
        class_id = self.child_prod_class1.pk
        params_list_page = self.list_page.params_list_subclass(class_id)
        params_list_url = reverse("classes:params_list", args=[class_id,])
        full_url = self.server_url + params_list_url
        params_list_page.check_url_is_correct(full_url)

    def test_products_list_subclass_btn_redirects_to_products_list_page(self):
        class_id = self.child_prod_class1.pk
        main_class_id = self.prod_class.pk
        products_list_page = self.list_page.products_list_subclass(class_id)
        products_list_url = reverse("products:class_products", kwargs={
            "main_class_id": main_class_id,
            "class_id": class_id
        })
        full_url = self.server_url + products_list_url
        products_list_page.check_url_is_correct(full_url)

    def test_delete_subclass_btn_redirects_to_delete_page(self):
        class_id = self.child_prod_class1.pk
        delete_page = self.list_page.delete_subclass(class_id)
        delete_url = reverse("classes:delete", args=[class_id])
        full_url = self.server_url + delete_url
        delete_page.check_url_is_correct(full_url)
