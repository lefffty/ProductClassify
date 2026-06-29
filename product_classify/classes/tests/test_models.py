from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db.models import QuerySet
from django.db import IntegrityError

from parametr.models import Parametr
from products.constants import INT_PARAMS
from ei.models import Ei

from ..models import ClassStruct, ParClass
from ..constants import PRODUCT_ID


class ClassStructModelTest(TestCase):
    @staticmethod
    def get_expected_model_error_message(model_name: str) -> str:
        return f"Expected model 'ClassStruct', got '{model_name}'"

    @staticmethod
    def get_class_methods_call_error_message(method_name: str) -> str:
        return f"ClassStruct.{method_name}() did not return a QuerySet instance"

    @staticmethod
    def get_expected_ids_error_message(expected_ids: set[int], actual_ids: set[int]):
        return f"Expected to get objects with ids {expected_ids}, but got {actual_ids}"

    @staticmethod
    def get_expected_length_error_message(
        expected_length: int, actual_length: int
    ) -> str:
        return f"Expected to get {expected_length} objects, but got {actual_length} objects"

    def test_create_with_minimal_requirements(self):
        obj = ClassStruct.objects.create(
            name="test_class",
            short_name="tc1",
            base_ei=None,
            main_class=None,
        )
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, "test_class")
        self.assertEqual(obj.short_name, "tc1")
        self.assertIsNone(obj.base_ei)
        self.assertIsNone(obj.main_class)

    def test_string_representation(self):
        class1 = ClassStruct(
            name="test_class1",
            short_name="tc1",
            base_ei=None,
            main_class=None,
        )
        msg = "Incorrect string representation of ClassStruct object"
        self.assertEqual(str(class1), "test_class1", msg)

    def test_products_returns_valid_queryset_and_valid_class(self):
        products = ClassStruct.products()
        msg1 = self.get_class_methods_call_error_message(ClassStruct.products.__name__)
        msg2 = self.get_expected_model_error_message(products.model)
        self.assertIsInstance(products, QuerySet, msg1)
        self.assertEqual(products.model, ClassStruct, msg2)

    def test_products_contains_expected_ids(self):
        products = ClassStruct.products()
        expected_ids = {1, 2, 3, 4, 5}
        actual_ids = set(products.values_list("id", flat=True))
        length_msg = self.get_expected_length_error_message(
            len(expected_ids), len(actual_ids)
        )
        msg = self.get_expected_ids_error_message(expected_ids, actual_ids)
        self.assertEqual(len(actual_ids), len(expected_ids), length_msg)
        self.assertSetEqual(actual_ids, expected_ids, msg)

    def test_terminal_product_classes_returns_queryset_and_valid_class(self):
        terminal_product_classes = ClassStruct.terminal_product_classes()
        msg1 = self.get_class_methods_call_error_message(
            ClassStruct.terminal_product_classes.__name__
        )
        msg2 = self.get_expected_model_error_message(terminal_product_classes.model)
        self.assertIsInstance(terminal_product_classes, QuerySet, msg1)
        self.assertEqual(terminal_product_classes.model, ClassStruct, msg2)

    def test_terminal_enum_classes_returns_queryset_and_valid_class(self):
        terminal_enum_classes = ClassStruct.terminal_enum_classes()
        msg1 = self.get_class_methods_call_error_message(
            ClassStruct.terminal_enum_classes.__name__
        )
        msg2 = self.get_expected_model_error_message(terminal_enum_classes.model)
        self.assertIsInstance(terminal_enum_classes, QuerySet, msg1)
        self.assertEqual(terminal_enum_classes.model, ClassStruct, msg2)

    def test_parametr_types_returns_queryset_and_valid_class(self):
        parametr_types = ClassStruct.parametr_types()
        msg1 = self.get_class_methods_call_error_message(
            ClassStruct.parametr_types.__name__
        )
        msg2 = self.get_expected_model_error_message(parametr_types.model)
        self.assertIsInstance(parametr_types, QuerySet, msg1)
        self.assertEqual(parametr_types.model, ClassStruct, msg2)

    def test_parametr_types_contains_expected_ids(self):
        parametr_types = ClassStruct.parametr_types()
        expected_ids = {15, 16, 18, 19, 27, 28}
        actual_ids = set(parametr_types.values_list("id", flat=True))
        msg = self.get_expected_ids_error_message(expected_ids, actual_ids)
        length_msg = self.get_expected_length_error_message(
            len(expected_ids), len(actual_ids)
        )
        self.assertEqual(len(actual_ids), len(expected_ids), length_msg)
        self.assertSetEqual(actual_ids, expected_ids, msg)

    def test_enum_classes_returns_queryset_and_valid_class(self):
        enum_classes = ClassStruct.enum_classes()
        msg1 = self.get_class_methods_call_error_message(
            ClassStruct.enum_classes.__name__
        )
        msg2 = self.get_expected_model_error_message(enum_classes.model)
        self.assertIsInstance(enum_classes, QuerySet, msg1)
        self.assertEqual(enum_classes.model, ClassStruct, msg2)

    def test_enum_classes_contains_expected_ids(self):
        enum_classes = ClassStruct.enum_classes()
        expected_ids = {15, 16, 18, 19}
        actual_ids = set(enum_classes.values_list("id", flat=True))
        length_msg = self.get_expected_length_error_message(
            len(expected_ids), len(actual_ids)
        )
        msg = self.get_expected_ids_error_message(expected_ids, actual_ids)
        self.assertEqual(len(actual_ids), len(expected_ids), length_msg)
        self.assertSetEqual(actual_ids, expected_ids, msg)

    def test_all_enum_classes_returns_queryset_and_valid_class(self):
        all_enum_classes = ClassStruct.all_enum_classes()
        msg1 = self.get_class_methods_call_error_message(
            ClassStruct.all_enum_classes.__name__
        )
        msg2 = self.get_expected_model_error_message(all_enum_classes.model)
        self.assertIsInstance(all_enum_classes, QuerySet, msg1)
        self.assertEqual(all_enum_classes.model, ClassStruct, msg2)


class ParClassModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        base_ei = Ei.objects.first()
        par_ei = Ei.objects.first()
        parametr_type = ClassStruct.objects.get(pk=INT_PARAMS)
        main_class = ClassStruct.objects.get(pk=PRODUCT_ID)
        cls.class_field = ClassStruct.objects.create(
            name="Products_class",
            short_name="Pc",
            base_ei=base_ei,
            main_class=main_class,
        )
        cls.parametr = Parametr.objects.create(
            name="Parametr",
            short_name="p",
            parametr_type=parametr_type,
            par_ei=par_ei,
        )

    def test_raises_validation_error_if_num_is_equal_to_zero(self):
        num = 0
        parclass = ParClass(
            class_field=self.class_field,
            parametr=self.parametr,
            min_value=1,
            max_value=100,
            num=num,
        )
        with self.assertRaises(ValidationError):
            parclass.full_clean()

    def test_raises_integrity_error_if_num_is_equal_to_zero(self):
        num = 0
        parclass = ParClass(
            class_field=self.class_field,
            parametr=self.parametr,
            min_value=1,
            max_value=100,
            num=num,
        )
        with self.assertRaises(IntegrityError):
            parclass.save()

    def test_valid_num_value_pass(self):
        num = 1
        parclass = ParClass(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=1,
            max_value=100,
        )
        parclass.full_clean()
        parclass.save()
        self.assertIsNotNone(parclass.pk)

    def test_clean_raises_error_if_max_less_than_min(self):
        num = 1
        parclass = ParClass(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=100,
            max_value=1,
        )
        with self.assertRaises(ValidationError) as ve:
            parclass.full_clean()
        self.assertIn("min_value", ve.exception.error_dict)
        self.assertIn("max_value", ve.exception.error_dict)

    def test_check_constraint_raises_integrity_error_if_max_less_than_min(self):
        num = 1
        parclass = ParClass(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=100,
            max_value=1,
        )
        with self.assertRaises(IntegrityError):
            parclass.save()

    def test_valid_values_pass(self):
        num = 1
        parclass = ParClass(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=1,
            max_value=100,
        )
        parclass.full_clean()
        parclass.save()
        self.assertIsNotNone(parclass.pk)

    def test_create_with_minimal_requirements(self):
        num = ParClass.objects.filter(class_field=self.class_field).count() + 1
        obj = ParClass.objects.create(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=1,
            max_value=100,
        )
        self.assertIsNotNone(obj.pk)

    def test_unique_constraints(self):
        num = 1
        ParClass.objects.create(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=1,
            max_value=100,
        )
        with self.assertRaises(IntegrityError):
            num += 1
            ParClass.objects.create(
                class_field=self.class_field,
                parametr=self.parametr,
                num=num,
                min_value=1,
                max_value=100,
            )

    def test_string_representation(self):
        num = ParClass.objects.filter(class_field=self.class_field).count() + 1
        obj = ParClass.objects.create(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=1,
            max_value=100,
        )
        expected_representation = "Products_class - Parametr"
        self.assertEqual(str(obj), expected_representation)

    def test_class_field_relationship(self):
        num = ParClass.objects.filter(class_field=self.class_field).count() + 1
        obj = ParClass.objects.create(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=1,
            max_value=100,
        )
        self.assertIn(obj, self.class_field.class_params.all())

    def test_parametr_relationship(self):
        num = ParClass.objects.filter(class_field=self.class_field).count() + 1
        obj = ParClass.objects.create(
            class_field=self.class_field,
            parametr=self.parametr,
            num=num,
            min_value=1,
            max_value=100,
        )
        self.assertIn(obj, self.parametr.parclass_set.all())
