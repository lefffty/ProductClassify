from django.test import TestCase
from django.urls import reverse

from faker import Faker

from classes.models import ClassStruct, ParClass
from classes.constants import NUTS_ID, CLASS_STRUCT_NAME_MAX_LENGTH, CLASS_STRUCT_SHORT_NAME_MAX_LENGTH

from parametr.models import Parametr
from parametr.constants import PARAMETR_NAME_MAX_LENGTH, PARAMETR_SHORT_NAME_MAX_LENGTH

from ei.models import Ei

from products.constants import PROD_NAME_MAX_LENGTH, PROD_SHORT_NAME_MAX_LENGTH
from products.models import Prod, ParProd, INT_PARAMS
from products.errors import *


class ProductDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.nuts_class = ClassStruct.objects.get(pk=NUTS_ID)
        cls.ei = Ei.objects.first()
        cls.int_params = ClassStruct.objects.get(pk=INT_PARAMS)
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )
        cls.parametr = Parametr.objects.create(
            name=cls.fake.name()[:PARAMETR_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:PARAMETR_SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_params,
            par_ei=cls.ei
        )
        cls.parclass = ParClass.objects.create(
            class_field=cls.prod_class,
            parametr=cls.parametr,
            num=1,
            min_value=10,
            max_value=20,
        )

        cls.prod = Prod.objects.create(
            name=cls.fake.name()[:PROD_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:PROD_SHORT_NAME_MAX_LENGTH],
            class_field=cls.prod_class,
            image=None,
        )
        cls.parprod = ParProd.objects.create(
            prod=cls.prod,
            par=cls.parametr,
            int_value=15,
            double_value=None,
            enum_val=None,
        )

        cls.url = reverse("products:product_detail", args=[cls.prod.pk])

    def test_product_detail_view_uses_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/detail.html")

    def test_product_detail_view_has_params_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("params", response.context)

    def test_product_detail_view_has_product_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("product", response.context)

    def test_product_detail_view_renders_correct_information_about_product(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.prod.pk)
        self.assertContains(response, self.prod.name)
        self.assertContains(response, self.prod.class_field.name)

    def test_product_detail_view_renders_correct_information_about_params(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.parametr.name)
        self.assertContains(response, self.parprod.value)


class ProductCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.nuts_class = ClassStruct.objects.get(pk=NUTS_ID)
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )

        name = cls.fake.name()[:PROD_NAME_MAX_LENGTH]
        short_name = cls.fake.name()[:PROD_SHORT_NAME_MAX_LENGTH]

        cls.data = {
            "name": name,
            "short_name": short_name,
            "class_field": cls.prod_class.pk,
            "image": "",
        }
        cls.empty_class_field_data = {
            "name": name,
            "short_name": short_name,
            "class_field": "",
            "image": ""
        }
        cls.empty_name_field_data = {
            "name": "",
            "short_name": short_name,
            "class_field": cls.prod_class.pk,
            "image": ""
        }

        cls.url = reverse("products:add_product")
        cls.redirect_url = reverse("classes:index")

    def test_product_create_view_uses_product_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/product.html")

    def test_product_create_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_product_create_view_can_save_a_POST_request(self):
        self.client.post(self.url, data=self.data)
        prod = Prod.objects.last()
        self.assertEqual(self.data["name"], prod.name)
        self.assertEqual(self.data["short_name"], prod.short_name)
        self.assertEqual(self.data["class_field"], prod.class_field.pk)
        self.assertEqual(self.data["image"], prod.image)

    def test_product_create_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_class_field_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_class_field_data)
        self.assertContains(response, ProdErrors.EMPTY_CLASS_FIELD)

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_name_field_data)
        self.assertContains(response, ProdErrors.EMPTY_NAME_FIELD)
