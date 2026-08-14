from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker
from PIL import Image
from io import BytesIO

from classes.models import ClassStruct, ParClass
from classes.constants import ProductsConsts, ClassStructConsts, ParamIds

from parametr.models import Parametr
from parametr.constants import ParametrConsts

from ei.models import Ei

from products.constants import ProdConsts
from products.models import Prod, ParProd
from products.errors import *


class ProductDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.ei = Ei.objects.first()
        cls.int_params = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )
        cls.parametr = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
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
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
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

        cls.url = reverse("products:detail", args=[cls.prod.pk])

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

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.FASTENER_ID)
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )

        name = cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH]
        short_name = cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]

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

        cls.url = reverse("products:add")
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


class ProductUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )

        old_name = cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH]
        old_short_name = cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]

        cls.prod = Prod.objects.create(
            name=old_name,
            short_name=old_short_name,
            class_field=cls.prod_class,
            image=None,
        )

        new_name = cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH]
        new_short_name = cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]

        cls.data = {
            "name": new_name,
            "short_name": new_short_name,
            "class_field": cls.prod_class.pk,
            "image": cls._create_test_image(),
        }
        cls.empty_class_field_data = {
            "name": new_name,
            "short_name": new_short_name,
            "class_field": "",
            "image": ""
        }
        cls.empty_name_field_data = {
            "name": "",
            "short_name": new_short_name,
            "class_field": cls.prod_class.pk,
            "image": ""
        }

        cls.url = reverse("products:edit", args=[cls.prod.pk])
        cls.redirect_url = reverse("products:detail", args=[cls.prod.pk])

    def _create_test_image(extension='jpg'):
        image = Image.new('RGB', (100, 100), color='red')
        file = BytesIO()
        format = 'JPEG' if extension == 'jpg' else 'PNG'
        image.save(file, format=format)
        file.seek(0)
        return SimpleUploadedFile(
            f"test.{extension}",
            file.read(),
            content_type=f"image/{extension if extension != 'jpg' else 'jpeg'}"
        )

    def test_product_update_view_uses_product_html(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/product.html")

    def test_product_update_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_product_update_view_has_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_product_update_view_can_save_a_POST_request(self):
        self.client.post(self.url, data=self.data)
        prod = Prod.objects.last()
        self.assertEqual(self.data["name"], prod.name)
        self.assertEqual(self.data["short_name"], prod.short_name)
        self.assertEqual(self.data["class_field"], prod.class_field.pk)
        self.assertIsNotNone(prod.image)

    def test_product_update_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_class_field_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_class_field_data)
        self.assertContains(response, ProdErrors.EMPTY_CLASS_FIELD)

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_name_field_data)
        self.assertContains(response, ProdErrors.EMPTY_NAME_FIELD)


class ProductDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.instance = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_class,
        )

        cls.url = reverse("products:delete", args=[cls.instance.pk])
        cls.redirect_url = reverse("products:class_products", kwargs={
            "main_class_id": cls.nuts_class.main_class.pk,
            "class_id": cls.nuts_class.pk,
        })

    def test_product_delete_view_uses_product_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/product.html")

    def test_product_delete_view_can_save_a_POST_request(self):
        count_before = Prod.objects.count()
        self.client.post(self.url)
        self.assertEqual(Prod.objects.count(), count_before - 1)

    def test_product_delete_view_redirects_after_POST_request(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)
