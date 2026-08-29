from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker

from tests.unit.base import BaseUnitTestCase

from classes.models import ClassStruct
from classes.constants import ProductsConsts, ProdClassConsts
from products.models import Prod
from products.constants import ProdConsts
from ei.models import Ei

from specifications.models import ProdComponent, SpecificationLogs


class ProdComponentTest(BaseUnitTestCase):
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
            base_ei=cls.base_ei,
        )
        cls.prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            ei=cls.base_ei,
            cost=400,
            modification=None,
            image=cls.image,
        )
        cls.component = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            ei=cls.base_ei,
            cost=400,
            modification=None,
            image=cls.image,
        )
        cls.prodcomponent1 = ProdComponent.objects.create(
            parent_prod=cls.prod,
            component=cls.component,
            num=1,
            quantity=12
        )

    def test_string_representation(self):
        actual_representation = str(self.prodcomponent1)
        expected_representation = f"{self.prod.name} - {self.component.name}"
        self.assertEqual(actual_representation, expected_representation)

    def test_is_parent_prod_returns_true_if_product_is_parent(self):
        is_parent = ProdComponent.is_parent_prod(self.prod.pk)
        self.assertEqual(is_parent, 1)

    def test_is_parent_prod_returns_false_if_product_is_not_parent(self):
        is_parent = ProdComponent.is_parent_prod(self.component.pk)
        self.assertEqual(is_parent, 0)

    def test_total_cost_ratio(self):
        quantity = 2
        total_cost_ratio = ProdComponent.total_cost_ratio(self.prod.pk, quantity)
        self.assertEqual(len(total_cost_ratio), 1)
        record = total_cost_ratio[0]
        self.assertEqual(record.parent_id, self.prod.pk)
        self.assertEqual(record.parent_prod_name, self.prod.name)
        self.assertEqual(record.child_id, self.component.pk)
        self.assertEqual(record.child_prod_name, self.component.name)
        self.assertEqual(record.quantity, self.prodcomponent1.quantity)
        self.assertEqual(record.ei_short_name, self.base_ei.short_name)
        self.assertEqual(record.total_cost, self.component.cost * quantity * self.prodcomponent1.quantity)
        self.assertEqual(record.level, 1)

    def test_product_specification(self):
        product_specification = ProdComponent.product_specification(self.prod.pk)
        self.assertEqual(len(product_specification), 1)
        record = product_specification[0]
        self.assertEqual(record.pair_id, self.prodcomponent1.pk)
        self.assertEqual(record.parent_id, self.prod.pk)
        self.assertEqual(record.child_id, self.component.pk)
        self.assertEqual(record.prod_num, 1)
        self.assertEqual(record.quantity, self.prodcomponent1.quantity)


class SpecificationLogsTest(BaseUnitTestCase):
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
            base_ei=cls.base_ei,
        )
        cls.prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            ei=cls.base_ei,
            cost=400,
            modification=None,
            image=cls.image,
        )
        cls.component = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            ei=cls.base_ei,
            cost=400,
            modification=None,
            image=cls.image,
        )
        cls.prodcomponent1 = ProdComponent.objects.create(
            parent_prod=cls.prod,
            component=cls.component,
            num=1,
            quantity=24
        )
        cls.logs1 = SpecificationLogs.objects.create(
            pair=cls.prodcomponent1,
            old_quantity=12,
            new_quantity=24,
        )

    def test_string_representation(self):
        actual_representation = str(self.logs1)
        expected_representation = f"Количество изделия {self.component.name} изменилось с {12} на {24}"
        self.assertEqual(actual_representation, expected_representation)

    def test_get_changelog(self):
        log_string = f'Количество изделия "{self.component.name}" для изделия "{self.prod.name}" изменилось с {self.logs1.old_quantity} на {self.logs1.new_quantity}'
        changelog = SpecificationLogs.get_changelog(self.prod.pk)
        self.assertEqual(len(changelog), 1)
        record = changelog[0]
        self.assertEqual(record.log_id, self.logs1.pk)
        self.assertEqual(record.parent_id, self.prod.pk)
        self.assertEqual(record.comp_id, self.component.pk)
        self.assertEqual(record.log_string, log_string)
        self.assertIsNotNone(record.updated_at)
