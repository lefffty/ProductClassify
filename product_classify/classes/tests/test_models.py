from django.test import TestCase
from django.db.models import QuerySet

from ..models import ClassStruct


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

    def test_string_representation(self):
        class1 = ClassStruct(
            name="test_class1",
            short_name="tc1",
            base_ei=None,
            main_class=None,
        )
        msg = "Incorrect string representation of ClassStruct"
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
        actual_ids = set(products.values_list('id', flat=True))
        msg = self.get_expected_ids_error_message(expected_ids, actual_ids)
        self.assertSetEqual(actual_ids, expected_ids, msg)

    def test_terminal_product_classes_returns_queryset_and_valid_class(self):
        terminal_product_classes = ClassStruct.terminal_product_classes()
        msg1 = self.get_class_methods_call_error_message(ClassStruct.terminal_product_classes.__name__)
        msg2 = self.get_expected_model_error_message(terminal_product_classes.model)
        self.assertIsInstance(terminal_product_classes, QuerySet, msg1)
        self.assertEqual(terminal_product_classes.model, ClassStruct, msg2)

    def test_terminal_enum_classes_returns_queryset_and_valid_class(self):
        terminal_enum_classes = ClassStruct.terminal_enum_classes()
        msg1 = self.get_class_methods_call_error_message(ClassStruct.terminal_enum_classes.__name__)
        msg2 = self.get_expected_model_error_message(terminal_enum_classes.model)
        self.assertIsInstance(terminal_enum_classes, QuerySet, msg1)
        self.assertEqual(terminal_enum_classes.model, ClassStruct, msg2)

    def test_parametr_types_returns_queryset_and_valid_class(self):
        parametr_types = ClassStruct.parametr_types()
        msg1 = self.get_class_methods_call_error_message(ClassStruct.parametr_types.__name__)
        msg2 = self.get_expected_model_error_message(parametr_types.model)
        self.assertIsInstance(parametr_types, QuerySet, msg1)
        self.assertEqual(parametr_types.model, ClassStruct, msg2)

    def test_parametr_types_contains_expected_ids(self):
        parametr_types = ClassStruct.parametr_types()
        expected_ids = {15, 16, 18, 19, 27, 28}
        actual_ids = set(parametr_types.values_list('id', flat=True))
        msg = self.get_expected_ids_error_message(expected_ids, actual_ids)
        self.assertSetEqual(actual_ids, expected_ids, msg)

    def test_enum_classes_returns_queryset_and_valid_class(self):
        enum_classes = ClassStruct.enum_classes()
        msg1 = self.get_class_methods_call_error_message(ClassStruct.enum_classes.__name__)
        msg2 = self.get_expected_model_error_message(enum_classes.model)
        self.assertIsInstance(enum_classes, QuerySet, msg1)
        self.assertEqual(enum_classes.model, ClassStruct, msg2)

    def test_enum_classes_contains_expected_ids(self):
        enum_classes = ClassStruct.enum_classes()
        expected_ids = {15, 16, 18, 19}
        actual_ids = set(enum_classes.values_list('id', flat=True))
        msg = self.get_expected_ids_error_message(expected_ids, actual_ids)
        self.assertSetEqual(actual_ids, expected_ids, msg)

    def test_all_enum_classes_returns_queryset_and_valid_class(self):
        all_enum_classes = ClassStruct.all_enum_classes()
        msg1 = self.get_class_methods_call_error_message(ClassStruct.all_enum_classes.__name__)
        msg2 = self.get_expected_model_error_message(all_enum_classes.model)
        self.assertIsInstance(all_enum_classes, QuerySet, msg1)
        self.assertEqual(all_enum_classes.model, ClassStruct, msg2)