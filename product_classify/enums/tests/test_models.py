from django.db import IntegrityError
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from classes.models import ClassStruct
from ..models import Enums
from ..constants import (
    INT_ENUMS_ID,
    IMAGE_ENUMS_ID,
    DOUBLE_ENUMS_ID,
    STRING_ENUMS_ID,
)


class EnumsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.image = SimpleUploadedFile(
            name="image.jpg",
            content=b"content",
            content_type="image/jpeg",
        )
        cls.int_enum = ClassStruct.objects.get(pk=INT_ENUMS_ID)
        cls.double_enum = ClassStruct.objects.get(pk=DOUBLE_ENUMS_ID)
        cls.string_enum = ClassStruct.objects.get(pk=STRING_ENUMS_ID)
        cls.image_enum = ClassStruct.objects.get(pk=IMAGE_ENUMS_ID)

        cls.int_enum_class = ClassStruct.objects.create(
            name="Test int enum class",
            short_name="test",
            base_ei=None,
            main_class=cls.int_enum,
        )
        cls.double_enum_class = ClassStruct.objects.create(
            name="Test double enum class",
            short_name="test",
            base_ei=None,
            main_class=cls.double_enum,
        )
        cls.string_enum_class = ClassStruct.objects.create(
            name="Test string enum class",
            short_name="test",
            base_ei=None,
            main_class=cls.string_enum,
        )
        cls.image_enum_class = ClassStruct.objects.create(
            name="Test image enum class",
            short_name="test",
            base_ei=None,
            main_class=cls.image_enum,
        )

    def test_create_with_minimal_requirements(self):
        num = 1
        value = Enums.objects.create(
            enum=self.double_enum_class,
            num=num,
            name="",
            short_name="",
            double_value=1.0,
            int_value=None,
            image=None,
        )
        self.assertIsNotNone(value.pk)

    def test_parent_class_relationship(self):
        num = 1
        value = Enums.objects.create(
            enum=self.int_enum_class,
            num=num,
            name="",
            short_name="",
            double_value=None,
            int_value=1,
            image=None,
        )
        self.assertEqual(value.enum, self.int_enum_class)
        self.assertIn(value, self.int_enum_class.class_enum_values.all())

    def test_image_field_path(self):
        num = 1
        value = Enums.objects.create(
            enum=self.image_enum_class,
            num=num,
            name="",
            short_name="",
            double_value=None,
            int_value=None,
            image=self.image,
        )
        self.assertTrue(value.image.name.startswith("enum_images/"))

    def test_string_representation_of_image_enum_value(self):
        num = 1
        value = Enums(
            enum=self.image_enum_class,
            num=num,
            name="Вариант исполнения1",
            short_name="ВарИсп1",
            double_value=None,
            int_value=None,
            image=self.image,
        )
        expected_representation = "ВарИсп1"
        self.assertEqual(str(value), expected_representation)

    def test_string_representation_of_string_enum_value(self):
        num = 1
        value = Enums(
            enum=self.string_enum_class,
            num=num,
            name="Строковое значение перечисления",
            short_name="СтрЗнач",
            double_value=None,
            int_value=None,
        )
        expected_representation = "СтрЗнач"
        self.assertEqual(str(value), expected_representation)

    def test_string_representation_of_integer_enum_value(self):
        num = 1
        value = Enums(
            enum=self.int_enum_class,
            num=num,
            name="Целочисленное значение",
            short_name="ЦелЗнач",
            double_value=None,
            int_value=1,
        )
        expected_representation = "ЦелЗнач - 1"
        self.assertEqual(str(value), expected_representation)

    def test_string_representation_of_double_enum_value(self):
        num = 1
        value = Enums(
            enum=self.double_enum_class,
            num=num,
            name="Вещественное значение",
            short_name="ВещЗнач",
            double_value=1.0,
            int_value=None,
        )
        expected_representation = "ВещЗнач - 1.0"
        self.assertEqual(str(value), expected_representation)

    def test_get_all_image_nums(self):
        num = 1
        Enums.objects.create(
            enum=self.image_enum_class,
            num=num,
            name="Вариант исполнения1",
            short_name="ВарИсп1",
            double_value=None,
            int_value=None,
            image=self.image,
        )
        image_enums = Enums.image_nums()
        self.assertEqual(image_enums.count(), 1)

    def test_get_all_string_enums(self):
        num = 1
        Enums.objects.create(
            enum=self.string_enum_class,
            num=num,
            name="Строковое значение перечисления",
            short_name="СтрЗнач",
            double_value=None,
            int_value=None,
        )
        string_enums = Enums.string_nums()
        self.assertEqual(string_enums.count(), 1)

    def test_get_all_integer_enums(self):
        num = 1
        Enums.objects.create(
            enum=self.int_enum_class,
            num=num,
            name="Целочисленное значение",
            short_name="ЦелЗнач",
            double_value=None,
            int_value=1,
        )
        int_enums = Enums.int_nums()
        self.assertEqual(int_enums.count(), 1)

    def test_get_all_double_enums(self):
        num = 1
        Enums.objects.create(
            enum=self.double_enum_class,
            num=num,
            name="Вещественное значение",
            short_name="ВещЗнач",
            double_value=1.0,
            int_value=None,
        )
        double_enums = Enums.double_nums()
        self.assertEqual(double_enums.count(), 1)

    def test_unique_together(self):
        Enums.objects.create(enum=self.int_enum_class, num=1)
        with self.assertRaises(IntegrityError):
            Enums.objects.create(enum=self.int_enum_class, num=1)