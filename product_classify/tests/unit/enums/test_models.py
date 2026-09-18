from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.unit.base import BaseUnitTestCase
from tests.unit.enums.factories.enums import EnumsFactory
from tests.unit.classes.factories.class_struct import ClassStructFactory

from classes.models import ClassStruct
from classes.constants import EnumsIds, ProductsConsts

from enums.models import Enums
from enums.errors import (
    EnumsErrors,
    IntEnumErrors,
    ImageEnumErrors,
    StringEnumErrors,
    DoubleEnumErrors,
)


class EnumsModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.image = SimpleUploadedFile(
            name="image.jpg",
            content=b"content",
            content_type="image/jpeg",
        )
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.double_enum = ClassStruct.objects.get(pk=EnumsIds.DOUBLE)
        cls.string_enum = ClassStruct.objects.get(pk=EnumsIds.STRING)
        cls.image_enum = ClassStruct.objects.get(pk=EnumsIds.IMAGE)

        cls.int_enum_class = ClassStructFactory(
            name="Test int enum class",
            short_name="test",
            main_class=cls.int_enum,
        )
        cls.double_enum_class = ClassStructFactory(
            name="Test double enum class",
            short_name="test",
            main_class=cls.double_enum,
        )
        cls.string_enum_class = ClassStructFactory(
            name="Test string enum class",
            short_name="test",
            main_class=cls.string_enum,
        )
        cls.image_enum_class = ClassStructFactory(
            name="Test image enum class",
            short_name="test",
            main_class=cls.image_enum,
        )
        cls.invalid_enum_class = ClassStruct.objects.get(pk=ProductsConsts.FASTENER_ID)

    def test_create_with_minimal_requirements(self):
        value = EnumsFactory(
            enum=self.double_enum_class,
            num=1,
            name="",
            short_name="",
            double_value=1.0,
        )
        self.assertIsNotNone(value.pk)

    def test_parent_class_relationship(self):
        value = EnumsFactory(
            enum=self.int_enum_class,
            num=1,
            name="",
            short_name="",
            int_value=1,
        )
        self.assertEqual(value.enum, self.int_enum_class)
        self.assertIn(value, self.int_enum_class.class_enum_values.all())

    def test_image_field_path(self):
        value = EnumsFactory(
            enum=self.image_enum_class,
            num=1,
            name="",
            short_name="",
            image=self.image,
        )
        self.assertTrue(value.image.name.startswith("enum_images/"))

    def test_string_representation_of_image_enum_value(self):
        value = EnumsFactory.build(
            enum=self.image_enum_class,
            num=1,
            name="Вариант исполнения1",
            short_name="ВарИсп1",
            image=self.image,
        )
        self.assertEqual(str(value), "ВарИсп1")

    def test_string_representation_of_string_enum_value(self):
        value = EnumsFactory.build(
            enum=self.string_enum_class,
            num=1,
            name="Строковое значение перечисления",
            short_name="СтрЗнач",
        )
        self.assertEqual(str(value), "СтрЗнач")

    def test_string_representation_of_integer_enum_value(self):
        value = EnumsFactory.build(
            enum=self.int_enum_class,
            num=1,
            name="Целочисленное значение",
            short_name="ЦелЗнач",
            int_value=1,
        )
        self.assertEqual(str(value), "1")

    def test_string_representation_of_double_enum_value(self):
        value = EnumsFactory.build(
            enum=self.double_enum_class,
            num=1,
            name="Вещественное значение",
            short_name="ВещЗнач",
            double_value=1.0,
        )
        self.assertEqual(str(value), "1.0")

    def test_get_all_image_nums(self):
        EnumsFactory(
            enum=self.image_enum_class,
            num=1,
            name="Вариант исполнения1",
            short_name="ВарИсп1",
            image=self.image,
        )
        self.assertEqual(Enums.image_nums().count(), 1)

    def test_get_all_string_enums(self):
        EnumsFactory(
            enum=self.string_enum_class,
            num=1,
            name="Строковое значение перечисления",
            short_name="СтрЗнач",
        )
        self.assertEqual(Enums.string_nums().count(), 1)

    def test_get_all_integer_enums(self):
        EnumsFactory(
            enum=self.int_enum_class,
            num=1,
            name="Целочисленное значение",
            short_name="ЦелЗнач",
            int_value=1,
        )
        self.assertEqual(Enums.int_nums().count(), 1)

    def test_get_all_double_enums(self):
        EnumsFactory(
            enum=self.double_enum_class,
            num=1,
            name="Вещественное значение",
            short_name="ВещЗнач",
            double_value=1.0,
        )
        self.assertEqual(Enums.double_nums().count(), 1)

    def test_unique_together(self):
        EnumsFactory(enum=self.int_enum_class, num=1)
        with self.assertRaises(IntegrityError):
            EnumsFactory(enum=self.int_enum_class, num=1)

    def test_raises_validation_error_if_enum_class_is_image_enum(self):
        enum = EnumsFactory.build(
            enum=self.image_enum_class,
            num=1,
            name="Image_enum_value",
            short_name="Image_enum_value",
            int_value=1,
            image=self.image,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(
            ve.exception.messages[0],
            ImageEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR,
        )

    def test_raises_validation_error_if_enum_class_is_string_enum(self):
        enum = EnumsFactory.build(
            enum=self.string_enum_class,
            num=1,
            name="String_enum_value",
            short_name="String_enum_value",
            int_value=1,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(
            ve.exception.messages[0],
            StringEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR,
        )

    def test_raises_validation_error_if_enum_class_is_int_enum(self):
        enum = EnumsFactory.build(
            enum=self.int_enum_class,
            num=1,
            name="Int_enum_value",
            short_name="Int_enum_value",
            int_value=1,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(
            ve.exception.messages[0],
            IntEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR,
        )

    def test_raises_validation_error_if_enum_class_is_double_enum(self):
        enum = EnumsFactory.build(
            enum=self.double_enum_class,
            num=1,
            name="Double_enum_value",
            short_name="Double_enum_value",
            double_value=1,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(
            ve.exception.messages[0],
            DoubleEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR,
        )

    def test_raises_validation_error_if_enum_class_is_not_enum(self):
        enum = EnumsFactory.build(
            enum=self.invalid_enum_class,
            num=1,
            name="Int_enum_value",
            short_name="Int_enum_value",
            int_value=1,
        )
        with self.assertRaises(ValidationError) as ve:
            enum.full_clean()
        self.assertEqual(ve.exception.messages[0], EnumsErrors.INVALID_PARENT)

    def test_value_property_for_int_enum(self):
        int_value = 1
        enum = EnumsFactory(
            enum=self.int_enum_class,
            num=1,
            name=None,
            short_name=None,
            int_value=int_value,
        )
        self.assertEqual(enum.value, int_value)

    def test_value_property_for_double_enum(self):
        double_value = 1.0
        enum = EnumsFactory(
            enum=self.double_enum_class,
            num=1,
            name=None,
            short_name=None,
            double_value=double_value,
        )
        self.assertEqual(enum.value, double_value)

    def test_value_property_for_string_enum(self):
        enum = EnumsFactory(
            enum=self.string_enum_class,
            num=1,
        )
        self.assertEqual(enum.value, enum.name)

    def test_value_property_for_image_enum(self):
        enum = EnumsFactory(
            enum=self.image_enum_class,
            num=1,
            name=None,
            short_name=None,
            image=self.image,
        )
        self.assertHasAttr(enum.value, "file")
