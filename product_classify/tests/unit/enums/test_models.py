from django.core.exceptions import ValidationError
from django.db import IntegrityError
from tests.unit.base import BaseUnitTestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker

from classes.models import ClassStruct
from classes.constants import EnumsIds, ProductsConsts

from enums.constants import EnumsConsts
from enums.models import Enums
from enums.errors import ImageEnumErrors, IntEnumErrors, StringEnumErrors, DoubleEnumErrors, EnumsErrors


class EnumsModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.image = SimpleUploadedFile(
            name="image.jpg",
            content=b"content",
            content_type="image/jpeg",
        )
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.double_enum = ClassStruct.objects.get(pk=EnumsIds.DOUBLE)
        cls.string_enum = ClassStruct.objects.get(pk=EnumsIds.STRING)
        cls.image_enum = ClassStruct.objects.get(pk=EnumsIds.IMAGE)

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
        cls.invalid_enum_class = ClassStruct.objects.get(pk=ProductsConsts.FASTENER_ID)

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
        expected_representation = "1"
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
        expected_representation = "1.0"
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
            image=None,
        )
        double_enums = Enums.double_nums()
        self.assertEqual(double_enums.count(), 1)

    def test_unique_together(self):
        Enums.objects.create(enum=self.int_enum_class, num=1)
        with self.assertRaises(IntegrityError):
            Enums.objects.create(enum=self.int_enum_class, num=1)

    def test_raises_validation_error_if_enum_class_is_image_enum(self):
        enum = Enums(
            enum=self.image_enum_class,
            num=1,
            name="Image_enum_value",
            short_name="Image_enum_value",
            double_value=None,
            int_value=1,
            image=self.image,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(ve.exception.messages[0], ImageEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)

    def test_raises_validation_error_if_enum_class_is_string_enum(self):
        enum = Enums(
            enum=self.string_enum_class,
            num=1,
            name="String_enum_value",
            short_name="String_enum_value",
            double_value=None,
            int_value=1,
            image=None,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(ve.exception.messages[0], StringEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)

    def test_raises_validation_error_if_enum_class_is_int_enum(self):
        enum = Enums(
            enum=self.int_enum_class,
            num=1,
            name="Int_enum_value",
            short_name="Int_enum_value",
            double_value=None,
            int_value=1,
            image=None,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(ve.exception.messages[0], IntEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)

    def test_raises_validation_error_if_enum_class_is_double_enum(self):
        enum = Enums(
            enum=self.double_enum_class,
            num=1,
            name="Double_enum_value",
            short_name="Double_enum_value",
            double_value=1,
            int_value=None,
            image=None,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(ve.exception.messages[0], DoubleEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR)

    def test_raises_validation_error_if_enum_class_is_not_enum(self):
        enum = Enums(
            enum=self.invalid_enum_class,
            num=1,
            name="Int_enum_value",
            short_name="Int_enum_value",
            double_value=None,
            int_value=1,
            image=None,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsErrors.INVALID_PARENT)

    def test_value_property_for_int_enum(self):
        int_value = 1
        enum = Enums.objects.create(
            name=None,
            short_name=None,
            num=1,
            enum=self.int_enum_class,
            double_value=None,
            image=None,
            int_value=int_value
        )
        self.assertEqual(enum.value, int_value)

    def test_value_property_for_double_enum(self):
        double_value = 1
        enum = Enums.objects.create(
            name=None,
            short_name=None,
            num=1,
            enum=self.double_enum_class,
            double_value=double_value,
            image=None,
            int_value=None,
        )
        self.assertEqual(enum.value, double_value)

    def test_value_property_for_string_enum(self):
        name = self.fake.name()[:EnumsConsts.NAME_MAX_LENGTH]
        short_name = self.fake.name()[:EnumsConsts.SHORT_NAME_MAX_LENGTH]
        enum = Enums.objects.create(
            name=name,
            short_name=short_name,
            num=1,
            enum=self.string_enum_class,
            double_value=None,
            image=None,
            int_value=None
        )
        self.assertEqual(enum.value, name)

    def test_value_property_for_image_enum(self):
        enum = Enums.objects.create(
            name=None,
            short_name=None,
            num=1,
            enum=self.image_enum_class,
            double_value=None,
            image=self.image,
            int_value=None
        )
        self.assertHasAttr(enum.value, "file")
