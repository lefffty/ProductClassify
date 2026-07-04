from django.test import TestCase
from django.db.models import QuerySet
from django.core.files.uploadedfile import SimpleUploadedFile

from typing import Literal, TypeAlias
from PIL import Image
from io import BytesIO

from classes.models import ClassStruct

from enums.models import Enums
from enums.forms import EnumsForm
from enums.constants import (
    STRING_ENUMS_ID,
    INT_ENUMS_ID,
    DOUBLE_ENUMS_ID,
    IMAGE_ENUMS_ID,
)

AllowedImageFormats: TypeAlias = Literal["jpg", "png"]


def create_test_image(extension: AllowedImageFormats = "jpg"):
    image = Image.new("RGB", (100, 100), "red")
    file = BytesIO()
    format = "JPEG" if extension == "jpg" else "PNG"
    image.save(file, format)
    file.seek(0)
    return SimpleUploadedFile(
        f"test.{extension}",
        file.read(),
        content_type=f"image/{extension if extension != 'jpg' else 'jpeg'}",
    )


class EnumsFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.string_enum_type = ClassStruct.objects.get(pk=STRING_ENUMS_ID)
        cls.int_enum_type = ClassStruct.objects.get(pk=INT_ENUMS_ID)
        cls.double_enum_type = ClassStruct.objects.get(pk=DOUBLE_ENUMS_ID)
        cls.image_enum_type = ClassStruct.objects.get(pk=IMAGE_ENUMS_ID)

        cls.non_terminal_enum = ClassStruct.objects.create(
            name="Не терминальный",
            short_name="NonTerm",
            main_class=None,
        )

        cls.string_enum = ClassStruct.objects.create(
            name="Вид резьбы",
            short_name="",
            main_class=cls.string_enum_type,
            base_ei=None,
        )
        cls.int_enum = ClassStruct.objects.create(
            name="Диаметр стержня",
            short_name="d",
            main_class=cls.int_enum_type,
            base_ei=None,
        )
        cls.double_enum = ClassStruct.objects.create(
            name="Высота головки",
            short_name="k",
            main_class=cls.double_enum_type,
            base_ei=None,
        )
        cls.image_enum = ClassStruct.objects.create(
            name="Вариант исполнения",
            short_name="ВарИсп",
            main_class=cls.image_enum_type,
            base_ei=None,
        )

        cls.JPG_IMAGE = create_test_image("jpg")
        cls.PNG_IMAGE = create_test_image("png")
        cls.INVALID_IMAGE = create_test_image("gif")

        cls.NAME = "Test name"
        cls.SHORT_NAME = "Test short name"
        cls.DOUBLE_VALUE = 1.5
        cls.NEW_DOUBLE_VALUE = 2.5
        cls.INT_VALUE = 1
        cls.INVALID_INT_VALUE = 0
        cls.INVALID_DOUBLE_VALUE = 0.0

    def test_enum_queryset_is_terminal_classes_queryset(self):
        """Проверяет, что поле enum в форме использует queryset из ClassStruct.terminal_enum_classes()."""
        terminal_enum_classes = ClassStruct.terminal_enum_classes()
        form = EnumsForm()
        self.assertIsInstance(form.fields["enum"].queryset, QuerySet)
        self.assertEqual(len(form.fields["enum"].queryset), len(terminal_enum_classes))

    def test_enum_field_is_required(self):
        """Проверяет, что поле enum обязательно для заполнения."""
        form_data = {
            "enum": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": self.DOUBLE_VALUE,
            "int_value": self.INT_VALUE,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        expected_error_msg = "Поле перечисления необходимо заполнить"

        form = EnumsForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn("enum", form.errors)
        self.assertEqual(form.errors["enum"][0], expected_error_msg)

    def test_non_terminal_enum_class_raises_validation_error(self):
        """Проверяет, что выбор enum, не входящего в terminal_enum_classes, вызывает ошибку валидации."""
        form_data = {
            "enum": self.int_enum_type,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_picture_value_field_is_optional_accepts_empty_string(self):
        """Проверяет, что поле picture_value может быть передано как пустая строка и форма проходит валидацию."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form_files = {
            "image": "",
        }
        form = EnumsForm(form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_picture_value_field_is_optional_accepts_none(self):
        """Проверяет, что поле picture_value может быть равно None и форма проходит валидацию."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form_files = {
            "image": None,
        }
        form = EnumsForm(form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_name_field_is_optional_accepts_empty_string(self):
        """Проверяет, что поле name может быть передано как пустая строка и форма проходит валидацию."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form_files = {
            "image": "",
        }
        form = EnumsForm(form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_name_field_is_optional_accepts_none(self):
        """Проверяет, что поле name может быть равно None и форма проходит валидацию."""
        form_data = {
            "enum": self.int_enum,
            "name": None,
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form_files = {
            "image": "",
        }
        form = EnumsForm(form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_double_field_is_optional_accepts_none(self):
        """Проверяет, что поле double_value может быть равно None и форма проходит валидацию."""
        form_data = {
            "enum": self.int_enum,
            "name": None,
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form_files = {
            "image": "",
        }
        form = EnumsForm(form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_int_field_is_optional_accepts_none(self):
        """Проверяет, что поле int_value может быть равно None и форма проходит валидацию."""
        form_data = {
            "enum": self.double_enum,
            "name": None,
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form_files = {
            "image": "",
        }
        form = EnumsForm(form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_negative_or_zero_value_for_int_value_is_invalid(self):
        """Проверяет, что отрицательное или нулевое значение int_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INVALID_INT_VALUE,
        }
        form_files = {
            "image": "",
        }
        form = EnumsForm(form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_negative_or_zero_value_for_double_value_is_invalid(self):
        """Проверяет, что отрицательное или нулевое значение double_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.INVALID_DOUBLE_VALUE,
            "int_value": None,
        }
        form_files = {
            "image": "",
        }
        form = EnumsForm(form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_jpg_extension_is_valid_for_picture_value(self):
        """Проверяет, что файлы с расширениями .jpg проходят валидацию как корректные изображения."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {
            "image": self.JPG_IMAGE,
        }
        form = EnumsForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid(), form.errors)

    def test_png_extension_is_valid_for_picture_value(self):
        """Проверяет, что файлы с расширениями .png проходят валидацию как корректные изображения."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = EnumsForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid(), form.errors)

    def test_not_jpg_or_png_is_not_valid(self):
        """Проверяет, что файлы с расширениями, отличными от .jpg и .png, не проходят валидацию."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {
            "image": self.INVALID_IMAGE,
        }
        form = EnumsForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid(), form.errors)

    def test_string_enums_value_does_not_have_name_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для строкового перечисления отсутствие значения в поле name вызывает ошибку валидации."""
        form_data = {
            "enum": self.string_enum,
            "name": "",
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_string_enums_value_does_not_have_short_name_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для строкового перечисления отсутствие значения в поле short_name вызывает ошибку валидации."""
        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_string_enums_value_has_picture_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для строкового перечисления заполнение поля picture_value приводит к ошибке валидации."""
        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = EnumsForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_string_enums_value_has_int_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для строкового перечисления заполнение поля int_value приводит к ошибке валидации."""
        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": self.INT_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_string_enums_value_has_double_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для строкового перечисления заполнение поля double_value приводит к ошибке валидации."""
        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": self.DOUBLE_VALUE,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_string_enums_value_form_is_valid(self):
        """Проверяет, что форма для строкового перечисления с корректными данными (только short_name и enum) валидна."""
        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_string_enums_value_is_saved_correctly(self):
        """Проверяет, что объект строкового перечисления создаётся и сохраняется с правильными значениями полей."""
        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.enum, form_data["enum"])
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.double_value, form_data["double_value"])
        self.assertEqual(obj.int_value, form_data["int_value"])
        self.assertIsNone(obj.image.name)

    def test_image_enums_value_value_does_not_have_picture_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для перечисления изображений отсутствие значения в поле picture_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_image_enums_value_double_field_filled_raises_validation_error(self):
        """Проверяет, что для перечисления изображений заполнение поля double_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_image_enums_value_int_field_filled_raises_validation_error(self):
        """Проверяет, что для перечисления изображений заполнение поля int_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_image_enums_value_picture_value_field_has_invalid_format_raises_validation_error(
        self,
    ):
        """Проверяет, что для перечисления изображений picture_value с недопустимым форматом (не .jpg/.png) вызывает ошибку."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.INVALID_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_image_enums_value_name_value_field_filled_does_not_raise_validation_error(
        self,
    ):
        """Проверяет, что для перечисления изображений заполнение поля 'Название' (name) не вызывает ошибку валидации."""
        form_data = {
            "enum": self.image_enum,
            "name": self.NAME,
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_image_enums_value_short_value_field_filled_does_not_raise_validation_error(
        self,
    ):
        """Проверяет, что для перечисления изображений заполнение поля 'Сокращенное название' (short_name) не вызывает ошибку валидации."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_image_enums_value_without_name_and_short_name_is_valid(self):
        """Проверяет, что для перечисления изображений поля name и short_name не обязательны."""
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.name, "")
        self.assertEqual(obj.short_name, "")

    def test_image_enums_value_form_is_valid(self):
        """Проверяет, что форма для перечисления изображений с корректными данными (name, short_name, enum, picture_value .jpg/.png) валидна."""
        form_data = {
            "enum": self.image_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_image_enums_value_is_saved_correctly(self):
        """Проверяет, что объект перечисления изображений создаётся и сохраняется с правильными значениями полей."""
        form_data = {
            "enum": self.image_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.enum, form_data["enum"])
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.double_value, form_data["double_value"])
        self.assertEqual(obj.int_value, form_data["int_value"])
        self.assertIsNotNone(obj.image.name)

    def test_int_enums_value_does_not_have_int_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для целочисленного перечисления отсутствие значения в поле int_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_int_enums_value_has_double_field_filled_raises_validation_error(self):
        """Проверяет, что для целочисленного перечисления заполнение поля double_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_int_enums_value_has_picture_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для целочисленного перечисления заполнение поля picture_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_int_enums_value_has_name_value_field_filled_raises_validation_error(self):
        """Проверяет, что для целочисленного перечисления заполнение поля name вызывает ошибку валидации."""
        form_data = {
            "enum": self.int_enum,
            "name": self.NAME,
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_int_enums_value_has_short_name_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для целочисленного перечисления заполнение поля short_name вызывает ошибку валидации."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_int_enums_value_form_is_valid(self):
        """Проверяет, что форма для целочисленного перечисления с корректными данными (enum, int_value) валидна."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_int_enums_value_is_saved_correctly(self):
        """Проверяет, что объект целочисленного перечисления создаётся и сохраняется с правильными значениями полей."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.enum, form_data["enum"])
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.double_value, form_data["double_value"])
        self.assertEqual(obj.int_value, form_data["int_value"])
        self.assertIsNone(obj.image.name)

    def test_double_enums_value_does_not_have_double_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для вещественного перечисления отсутствие значения в поле double_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_double_enums_value_has_int_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для вещественного перечисления заполнение поля int_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form = EnumsForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_double_enums_value_has_picture_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для вещественного перечисления заполнение поля picture_value вызывает ошибку валидации."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_double_enums_value_has_name_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для вещественного перечисления заполнение поля name вызывает ошибку валидации."""
        form_data = {
            "enum": self.double_enum,
            "name": self.NAME,
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_double_enums_value_has_short_name_value_field_filled_raises_validation_error(
        self,
    ):
        """Проверяет, что для вещественного перечисления заполнение поля short_name вызывает ошибку валидации."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_double_enums_value_form_is_valid(self):
        """Проверяет, что форма для вещественного перечисления с корректными данными (enum, double_value) валидна."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_double_enums_value_is_saved_correctly(self):
        """Проверяет, что объект вещественного перечисления создаётся и сохраняется с правильными значениями полей."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.enum, form_data["enum"])
        self.assertEqual(obj.double_value, form_data["double_value"])
        self.assertEqual(obj.int_value, form_data["int_value"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.name, form_data["name"])
        self.assertIsNone(obj.image.name)

    def test_class_struct_model_relationship(self):
        """Проверяет, что связь с моделью ClassStruct (через поле enum) работает корректно при сохранении."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIn(obj, self.double_enum.class_enum_values.all())

    def test_num_is_calculated_correctly_on_create(self):
        """Проверяет, что при создании нового объекта поле num вычисляется как count(enum)+1."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 1)

    def test_edit_without_changing_enum_class_is_saved_correctly(self):
        """Проверяет, что при редактировании без смены родительского enum все поля обновляются корректно."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.NEW_DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data, instance=obj)
        obj = form.save()
        self.assertEqual(obj.double_value, self.NEW_DOUBLE_VALUE)

    def test_num_is_not_overwritten_on_edit(self):
        """Проверяет, что при редактировании существующего объекта поле num не пересчитывается заново."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 1)

        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.NEW_DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data, instance=obj)
        obj = form.save()
        self.assertEqual(obj.num, 1)

    def test_edit_num_recalculated_on_enum_change(self):
        """Проверяет, что при смене enum num пересчитывается для нового родителя."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 1)

        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form = EnumsForm(data=form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 1)

    def test_edit_invalid_picture_for_image_enum_raises_error(self):
        """Проверяет, что при редактировании типа изображение нельзя оставить picture_value невалидным."""
        initial_form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        initial_form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=initial_form_data, files=initial_form_files)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.INVALID_IMAGE}
        form = EnumsForm(data=form_data, files=form_files, instance=obj)
        self.assertFalse(form.is_valid())

    def test_edit_without_new_image_keeps_old_image(self):
        """Проверяет, что при редактировании без загрузки нового изображения старый файл сохраняется."""
        initial_form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        initial_form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=initial_form_data, files=initial_form_files)
        self.assertTrue(form.is_valid())
        obj = form.save()
        old_image_name = obj.image.name

        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data, instance=obj)
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.image.name, old_image_name)

    def test_string_enums_value_edit_updates_fields(self):
        """Проверяет, что при редактировании строкового перечисления поля name и short_name обновляются."""
        form_data = {
            "enum": self.string_enum,
            "name": "Old Name",
            "short_name": "Old Short",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.name, self.NAME)
        self.assertEqual(obj.short_name, self.SHORT_NAME)

    def test_image_enums_value_edit_replace_image(self):
        """Проверяет, что при редактировании можно заменить изображение на другое корректное."""
        # Создаём с PNG
        form_data = {
            "enum": self.image_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form_files = {"image": self.PNG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())
        obj = form.save()
        old_image_name = obj.image.name

        form_files = {"image": self.JPG_IMAGE}
        form = EnumsForm(data=form_data, files=form_files, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertNotEqual(obj.image.name, old_image_name)  # имя изменилось
        self.assertTrue(obj.image.name.endswith(".jpg"))

    def test_int_enums_value_edit_updates_int_value(self):
        """Проверяет, что при редактировании целочисленного перечисления поле int_value обновляется."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": 5,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data["int_value"] = 10
        form = EnumsForm(data=form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.int_value, 10)

    def test_double_enums_value_edit_updates_double_value(self):
        """Проверяет, что при редактировании вещественного перечисления поле double_value обновляется."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": 1.5,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data["double_value"] = 2.7
        form = EnumsForm(data=form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.double_value, 2.7)

    def test_num_calculated_correctly_when_objects_exist(self):
        """Проверяет, что при создании нового объекта, когда уже есть записи для данного enum, num вычисляется как count(enum)+1."""
        Enums.objects.create(enum=self.double_enum, num=1, short_name="First")
        Enums.objects.create(enum=self.double_enum, num=2, short_name="Second")

        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 3)

    def test_edit_int_enum_removing_int_value_raises_error(self):
        """Проверяет, что при редактировании целочисленного перечисления нельзя удалить int_value (передать None)."""
        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": self.INT_VALUE,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data = {
            "enum": self.int_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data, instance=obj)
        self.assertFalse(form.is_valid())

    def test_edit_double_enum_removing_double_value_raises_error(self):
        """Проверяет, что при редактировании вещественного перечисления нельзя удалить double_value (передать None)."""
        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": self.DOUBLE_VALUE,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data = {
            "enum": self.double_enum,
            "name": "",
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data, instance=obj)
        self.assertFalse(form.is_valid())

    def test_edit_string_enum_removing_name_raises_error(self):
        """Проверяет, что при редактировании строкового перечисления нельзя удалить name (передать пустую строку или None)."""
        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data = {
            "enum": self.string_enum,
            "name": "",
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data, instance=obj)
        self.assertFalse(form.is_valid())

    def test_edit_string_enum_removing_short_name_raises_error(self):
        """Проверяет, что при редактировании строкового перечисления нельзя удалить short_name."""
        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        form_data = {
            "enum": self.string_enum,
            "name": self.NAME,
            "short_name": "",
            "double_value": None,
            "int_value": None,
        }
        form = EnumsForm(data=form_data, instance=obj)
        self.assertFalse(form.is_valid())