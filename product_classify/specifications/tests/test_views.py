from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from urllib.parse import quote
from http import HTTPStatus
from faker import Faker

from classes.models import ClassStruct
from classes.constants import ProductsConsts, ProdClassConsts

from ei.models import Ei

from products.models import Prod
from products.constants import ProdConsts

from specifications.models import ProdComponent, SpecificationLogs


class GetTotalCostRatioViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.parent_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.component_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.prodcomponent = ProdComponent.objects.create(
            parent_prod=cls.parent_prod,
            component=cls.component_prod,
            num=1,
            quantity=200,
        )

        cls.url = reverse("specifications:total_cost_ratio", args=[cls.parent_prod.pk])

    def test_get_total_cost_ratio_returns_ok_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_total_cost_ratio_content_type(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response["content-type"],
            "application/pdf"
        )

    def test_get_total_cost_ratio_filename(self):
        filename = f"Спецификация_изделия_{self.parent_prod.name}.pdf"
        encoded_filename = quote(filename, safe="")
        response = self.client.get(self.url)
        self.assertIn(
            f"filename*=utf-8''{encoded_filename}",
            response["Content-Disposition"]
        )


class GetProductChangelogViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.parent_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.component_prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=400,
            modification=None,
            ei=cls.base_ei,
        )
        cls.prodcomponent = ProdComponent.objects.create(
            parent_prod=cls.parent_prod,
            component=cls.component_prod,
            num=1,
            quantity=200,
        )
        cls.log = SpecificationLogs.objects.create(
            pair=cls.prodcomponent,
            old_quantity=100,
            new_quantity=200,
        )

        cls.url = reverse("specifications:changelog", args=[cls.parent_prod.pk])

    def test_get_product_changelog_returns_ok_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_product_changelog_content_type(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response["content-type"],
            "application/pdf"
        )        

    def test_get_product_changelog_filename(self):
        filename = f"История_изменений_спецификации_изделия_{self.parent_prod.name}.pdf"
        encoded_filename = quote(filename, safe="")        
        response = self.client.get(self.url)
        self.assertIn(
            f"filename*=utf-8''{encoded_filename}",
            response["Content-Disposition"]
        )
