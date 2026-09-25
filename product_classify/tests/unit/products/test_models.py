from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

from decimal import Decimal

from tests.unit.specifications.factories.prod_component import ProdComponentFactory
from tests.unit.base import BaseUnitTestCase
from tests.unit.classes.factories.class_struct import ClassStructFactory
from tests.unit.products.factories.product import ProdFactory
from tests.unit.products.factories.par_prod import ParProdFactory
from tests.unit.parametr.factories.parametr import ParametrFactory
from tests.unit.enums.factories.enums import EnumsFactory
from tests.unit.classes.factories.parclass import ParClassFactory

from ei.models import Ei
from classes.constants import ParamIds, ProductsConsts, EnumsIds
from classes.models import ClassStruct
from specifications.models import ProdComponent
from products.errors import CommonParProdErrors, EnumsParErrors, IntParErrors, DoubleParErrors
from products.models import Prod


class ProdModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.main_class = ClassStructFactory(
            name="main_class",
            short_name="main_cl",
        )
        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        cls.ei = Ei.objects.first()

    def test_create_with_minimal_requirements(self):
        prod = ProdFactory(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=self.image,
        )
        self.assertIsNotNone(prod.pk)

    def test_string_representation(self):
        prod = ProdFactory.build(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=self.image,
        )
        self.assertEqual(str(prod), "test")

    def test_image_field_path(self):
        prod = ProdFactory(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=self.image,
        )
        self.assertTrue(prod.image.name.startswith("product_images/"))

    def test_class_field_relation(self):
        prod = ProdFactory(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=self.image,
        )
        self.assertEqual(prod.class_field, self.main_class)
        self.assertIn(prod, self.main_class.class_products.all())

    def test_ei_relationship(self):
        prod = ProdFactory(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=self.image,
            ei=self.ei,
        )
        self.assertIn(prod, self.ei.prod_set.all())

    def test_negative_cost_value_raises_intergity_error(self):
        prod = ProdFactory.build(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=self.image,
            cost=Decimal("-1.0"),
            ei=None,
        )
        with self.assertRaises(ValidationError):
            prod.full_clean()

    def test_create_modification(self):
        prod = ProdFactory(
            name="Test prod",
            short_name="Test short",
            class_field=self.main_class,
            image=self.image,
            cost=Decimal("320000.00"),
            ei=self.ei,
        )
        component_prod = ProdFactory(
            name="Component prod",
            short_name="Comp short",
            class_field=self.main_class,
            image=self.image,
            cost=800,
            ei=self.ei,
        )
        ProdComponent.objects.create(
            parent_prod=prod,
            component=component_prod,
            num=1,
            quantity=400,
        )
        mod_name = "Mod name"
        mod_short_name = "Mod short"
        data = Prod.create_modification(prod.pk, mod_name, mod_short_name)
        modification = Prod.objects.get(pk=data.modification_id)
        self.assertEqual(modification.modification.pk, prod.pk)
        self.assertEqual(modification.image, prod.image)
        self.assertEqual(modification.cost, prod.cost)
        self.assertEqual(modification.ei, prod.ei)
        self.assertEqual(modification.name, mod_name)
        self.assertEqual(modification.short_name, mod_short_name)
        self.assertEqual(
            ProdComponent.objects.filter(parent_prod=modification.pk).count(), 1
        )


class ParProdModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        par_ei = Ei.objects.first()
        base_ei = Ei.objects.order_by("id")[1]
        fastener_class = ClassStruct.objects.get(pk=ProductsConsts.FASTENER_ID)

        cls.class_field = ClassStructFactory(
            name="products_class",
            short_name="prod_cls",
            base_ei=base_ei,
            main_class=fastener_class,
        )

        # типы параметров
        cls.int_parametr_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.double_parametr_type = ClassStruct.objects.get(pk=ParamIds.DOUBLE)
        cls.string_enum_type = ClassStruct.objects.get(pk=EnumsIds.STRING)
        cls.image_enum_type = ClassStruct.objects.get(pk=EnumsIds.IMAGE)
        cls.double_enum_type = ClassStruct.objects.get(pk=EnumsIds.DOUBLE)
        cls.int_enum_type = ClassStruct.objects.get(pk=EnumsIds.INT)

        # классы перечислений
        cls.int_enum_class = ClassStructFactory(
            name="int_enum_class",
            short_name="int_enum",
            base_ei=base_ei,
            main_class=cls.int_enum_type,
        )
        cls.double_enum_class = ClassStructFactory(
            name="double_enum_class",
            short_name="double_enum",
            base_ei=base_ei,
            main_class=cls.double_enum_type,
        )
        cls.string_enum_class = ClassStructFactory(
            name="string_enum_class",
            short_name="string_enum",
            base_ei=base_ei,
            main_class=cls.string_enum_type,
        )
        cls.image_enum_class = ClassStructFactory(
            name="image_enum_class",
            short_name="image_enum",
            base_ei=base_ei,
            main_class=cls.image_enum_type,
        )

        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.prod = ProdFactory(
            name="test_prod",
            short_name="test",
            class_field=cls.class_field,
            image=cls.image,
        )

        # параметры
        cls.int_parametr = ParametrFactory(
            name="int_parametr",
            short_name="int_par",
            parametr_type=cls.int_parametr_type,
            par_ei=par_ei,
        )
        cls.double_parametr = ParametrFactory(
            name="double_parametr",
            short_name="double_par",
            parametr_type=cls.double_parametr_type,
            par_ei=par_ei,
        )
        cls.string_enum_parametr = ParametrFactory(
            name="string_enum_parametr",
            short_name="str_enum_par",
            parametr_type=cls.string_enum_type,
            par_ei=par_ei,
        )
        cls.image_enum_parametr = ParametrFactory(
            name="image_enum_parametr",
            short_name="image_enum_par",
            parametr_type=cls.image_enum_type,
            par_ei=None,
        )
        cls.double_enum_parametr = ParametrFactory(
            name="double_enum_parametr",
            short_name="double_enum_par",
            parametr_type=cls.double_enum_type,
            par_ei=par_ei,
        )
        cls.int_enum_parametr = ParametrFactory(
            name="int_enum_parametr",
            short_name="int_enum_par",
            parametr_type=cls.int_enum_type,
            par_ei=par_ei,
        )
        cls.invalid_parametr = ParametrFactory(
            name="invalid_parametr",
            short_name="invalid_par",
            parametr_type=cls.int_parametr_type,
            par_ei=par_ei,
        )

        # значения перечислений
        cls.string_enum_value = EnumsFactory(
            enum=cls.string_enum_class,
            num=1,
            name="string_enum_value",
            short_name="string_enum",
        )
        cls.image_enum_value = EnumsFactory(
            enum=cls.image_enum_class,
            num=1,
            name="image_enum_value",
            short_name="string_enum",
            image=cls.image,
        )
        cls.int_enum_value = EnumsFactory(
            enum=cls.int_enum_class,
            num=1,
            name="int_enum_value",
            short_name="int_enum",
            int_value=1,
        )
        cls.double_enum_value = EnumsFactory(
            enum=cls.double_enum_class,
            num=1,
            name="double_enum_value",
            short_name="double_enum",
            double_value=1.0,
        )

        # ParClass для каждого типа параметра
        cls.double_parametr_parclass = ParClassFactory(
            class_field=cls.class_field,
            parametr=cls.double_parametr,
            num=1,
            min_value=1.0,
            max_value=5.0,
        )
        cls.int_parametr_parclass = ParClassFactory(
            class_field=cls.class_field,
            parametr=cls.int_parametr,
            num=2,
            min_value=1,
            max_value=5,
        )
        cls.string_enum_parametr_parclass = ParClassFactory(
            class_field=cls.class_field,
            parametr=cls.string_enum_parametr,
            num=3,
        )
        cls.image_enum_parametr_parclass = ParClassFactory(
            class_field=cls.class_field,
            parametr=cls.image_enum_parametr,
            num=4,
        )
        cls.double_enum_parametr_parclass = ParClassFactory(
            class_field=cls.class_field,
            parametr=cls.double_enum_parametr,
            num=5,
        )
        cls.int_enum_parametr_parclass = ParClassFactory(
            class_field=cls.class_field,
            parametr=cls.int_enum_parametr,
            num=6,
        )

        cls.double_val = 3.14

    def test_clean_raises_validation_error_if_parametr_does_not_belong_to_product_class(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.invalid_parametr,
            int_value=1,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = CommonParProdErrors.INVALID_PAR.format(self.invalid_parametr.name, self.class_field.name)
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_string_enum_value_is_absent(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.string_enum_parametr,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_string_enum_value_does_not_belong_to_string_enum_class(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.string_enum_parametr,
            enum_val=self.image_enum_value,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_image_enum_value_is_absent(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.image_enum_parametr,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_image_enum_value_does_not_belong_to_image_enum_class(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.image_enum_parametr,
            enum_val=self.string_enum_value,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_int_enum_value_is_absent(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.int_enum_parametr,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_int_enum_value_does_not_belong_to_int_enum_class(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.int_enum_parametr,
            enum_val=self.image_enum_value,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_double_enum_value_is_absent(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.double_enum_parametr,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_double_enum_value_does_not_belong_to_double_enum_class(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.double_enum_parametr,
            enum_val=self.string_enum_value,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_double_value_is_absent(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.double_parametr,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], DoubleParErrors.DOUBLE_FIELD_EMPTY)

    def test_clean_raises_validation_error_if_int_value_is_absent(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.int_parametr,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        self.assertEqual(ve.exception.messages[0], IntParErrors.INT_FIELD_EMPTY)

    def test_create_object_with_minimum_requirements(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.int_parametr,
            int_value=1,
        )
        self.assertIsNotNone(parprod.pk)

    def test_product_relationship(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.int_parametr,
            int_value=1,
        )
        self.assertIn(parprod, self.prod.product_params.all())

    def test_parametr_relationship(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.int_parametr,
            int_value=1,
        )
        self.assertIn(parprod, self.int_parametr.parprod_set.all())

    def test_enum_val_relationship(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.int_enum_parametr,
            enum_val=self.int_enum_value,
        )
        self.assertIsNotNone(parprod.pk)

    def test_unique_constraint(self):
        ParProdFactory(
            prod=self.prod,
            par=self.int_enum_parametr,
            enum_val=self.int_enum_value,
        )
        with self.assertRaises(IntegrityError):
            ParProdFactory(
                prod=self.prod,
                par=self.int_enum_parametr,
                enum_val=self.int_enum_value,
            )

    def test_clean_valid_for_int_parametr(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.int_parametr,
            int_value=5,
        )
        parprod.full_clean()

    def test_clean_valid_for_double_parametr(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.double_parametr,
            double_value=self.double_val,
        )
        parprod.full_clean()

    def test_clean_valid_for_string_enum(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.string_enum_parametr,
            enum_val=self.string_enum_value,
        )
        parprod.full_clean()

    def test_clean_valid_for_image_enum(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.image_enum_parametr,
            enum_val=self.image_enum_value,
        )
        parprod.full_clean()

    def test_clean_valid_for_int_enum(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.int_enum_parametr,
            enum_val=self.int_enum_value,
        )
        parprod.full_clean()

    def test_clean_valid_for_double_enum(self):
        parprod = ParProdFactory.build(
            prod=self.prod,
            par=self.double_enum_parametr,
            enum_val=self.double_enum_value,
        )
        parprod.full_clean()

    def test_create_without_full_clean_does_not_validate(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.string_enum_parametr,
        )
        self.assertIsNotNone(parprod.pk)
        with self.assertRaises(ValidationError):
            parprod.full_clean()

    def test_string_representation_for_int_parametr(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.int_parametr,
            int_value=5,
        )
        expected = f"{self.prod.name} - {self.int_parametr.name} - 5"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_double_parametr(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.double_parametr,
            double_value=self.double_val,
        )
        expected = f"{self.prod.name} - {self.double_parametr.name} - 3.14"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_int_enum_value(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.int_enum_parametr,
            enum_val=self.int_enum_value,
        )
        expected = f"{self.prod.name} - {self.int_enum_value.short_name} - {self.int_enum_value.int_value}"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_double_enum_value(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.double_enum_parametr,
            enum_val=self.double_enum_value,
        )
        expected = f"{self.prod.name} - {self.double_enum_value.short_name} - {self.double_enum_value.double_value}"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_string_enum_value(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.string_enum_parametr,
            enum_val=self.string_enum_value,
        )
        expected = f"{self.prod.name} - {self.string_enum_value.name}"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_image_enum_value(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.image_enum_parametr,
            enum_val=self.image_enum_value,
        )
        expected = f"{self.prod.name} - {self.image_enum_value.short_name}"
        self.assertEqual(str(parprod), expected)

    def test_get_value_for_int_parametr(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.int_parametr,
            int_value=5,
        )
        self.assertEqual(parprod.value, 5)

    def test_get_value_for_double_parametr(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.double_parametr,
            double_value=self.double_val,
        )
        self.assertEqual(parprod.value, self.double_val)

    def test_get_value_for_string_enum_value(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.string_enum_parametr,
            enum_val=self.string_enum_value,
        )
        self.assertEqual(parprod.value, self.string_enum_value.name)

    def test_get_value_for_int_enum_value(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.int_enum_parametr,
            enum_val=self.int_enum_value,
        )
        self.assertEqual(parprod.value, self.int_enum_value.int_value)

    def test_get_value_for_double_enum_value(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.double_enum_parametr,
            enum_val=self.double_enum_value,
        )
        self.assertEqual(parprod.value, self.double_enum_value.double_value)

    def test_get_value_for_image_enum_value(self):
        parprod = ParProdFactory(
            prod=self.prod,
            par=self.image_enum_parametr,
            enum_val=self.image_enum_value,
        )
        self.assertEqual(parprod.value, self.image_enum_value.image)


class ProdPriceRecalculationTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStructFactory(main_class=cls.nuts_class)

        cls.prod_c = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("10.00"), ei=cls.ei,
        )
        cls.prod_b = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("30.00"), ei=cls.ei,
        )
        cls.prod_a = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("60.00"), ei=cls.ei,
        )

        cls.pc_bc = ProdComponentFactory(
            parent_prod=cls.prod_b, component=cls.prod_c,
            num=1, quantity=Decimal("3.00"),
        )
        cls.pc_ab = ProdComponentFactory(
            parent_prod=cls.prod_a, component=cls.prod_b,
            num=1, quantity=Decimal("2.00"),
        )

    def test_child_cost_change_causes_recalculation_of_direct_parent_cost(self):
        self.prod_c.cost = 5
        self.prod_c.save(update_fields=["cost"])
        self.prod_b.refresh_from_db()

        self.assertEqual(self.prod_b.cost, Decimal("15.00"))
        

    def test_child_cost_change_causes_recalculation_of_all_ancestors(self):
        self.prod_c.cost = 5
        self.prod_c.save(update_fields=["cost"])

        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_a.cost, Decimal("30.00"))

    def test_no_recalculation_if_cost_did_not_change(self):
        self.prod_c.save(update_fields=["cost"])

        self.prod_b.refresh_from_db()
        self.prod_a.refresh_from_db()

        self.assertEqual(self.prod_a.cost, Decimal("60.00"))
        self.assertEqual(self.prod_b.cost, Decimal("30.00"))


class ProdCostRecalculationOnQuantityChangeTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStructFactory(main_class=cls.nuts_class)

        cls.prod_d = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("5.00"), ei=cls.ei,
        )
        cls.prod_c = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("10.00"), ei=cls.ei,
        )
        cls.prod_b = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("30.00"), ei=cls.ei,
        )
        cls.prod_a = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("60.00"), ei=cls.ei,
        )

        cls.pc_bc = ProdComponentFactory(
            parent_prod=cls.prod_b, component=cls.prod_c,
            num=1, quantity=Decimal("3.00"),
        )
        cls.pc_ab = ProdComponentFactory(
            parent_prod=cls.prod_a, component=cls.prod_b,
            num=1, quantity=Decimal("2.00"),
        )

    def test_quantity_updating_recalculates_parent_price(self):
        self.pc_bc.quantity = Decimal("1.00")
        self.pc_bc.save(update_fields=["quantity"])

        self.prod_b.refresh_from_db()
        self.assertEqual(self.prod_b.cost, Decimal("10.00"))

    def test_quantity_updating_causes_cascade_prices_calculations(self):
        self.pc_bc.quantity = Decimal("1.00")
        self.pc_bc.save(update_fields=["quantity"])

        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_a.cost, Decimal("20.00"))

    def test_adding_component_recalculates_prices(self):
        self.pc_bd = ProdComponentFactory(
            parent_prod=self.prod_b, component=self.prod_d,
            num=1, quantity=Decimal("1.00"),            
        )

        self.prod_b.refresh_from_db()
        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_b.cost, Decimal("35.00"))
        self.assertEqual(self.prod_a.cost, Decimal("70.00"))

    def test_deleting_component_recalculates_prices(self):
        self.pc_bd = ProdComponentFactory(
            parent_prod=self.prod_b, component=self.prod_d,
            num=1, quantity=Decimal("1.00"),            
        )

        self.pc_bd.delete()

        self.prod_b.refresh_from_db()
        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_b.cost, Decimal("30.00"))
        self.assertEqual(self.prod_a.cost, Decimal("60.00"))
