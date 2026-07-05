from django.test import TestCase
from django.db.models import QuerySet
from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image
from io import BytesIO

from classes.models import ClassStruct
from classes.constants import NUTS_ID
from enums.constants import STRING_ENUMS_ID

from products.forms import ProdForm


def create_image(extension: str = "jpg"):
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


class ProdFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.NUTS_CLASS = ClassStruct.objects.get(pk=NUTS_ID)
        cls.INVALID_CLASS = ClassStruct.objects.get(pk=STRING_ENUMS_ID)

        cls.PNG_IMAGE = create_image("png")
        cls.JPG_IMAGE = create_image("jpg")
        cls.GIF_IMAGE = create_image("gif")

        cls.PROD_NAME = "Test product name"
        cls.PROD_SHORT_NAME = "Test sh. name"
        cls.NEW_PROD_NAME = "New test product name"
        cls.NEW_PROD_SHORT_NAME = "New sh. nm."

    def test_class_field_queryset_is_products_classes(self):
        """Проверяет, что поле class_field использует queryset с объектами ClassStruct.products()."""
        form = ProdForm()
        self.assertIsInstance(form.fields["class_field"].queryset, QuerySet)
        self.assertEqual(len(form.fields["class_field"].queryset), 5)

    def test_class_field_is_required(self):
        """Проверяет, что поле class_field обязательно для заполнения."""
        form_data = {
            "class_field": None,
            "name": self.PROD_NAME,
            "short_name": None,
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn(
            form.errors["class_field"][0],
            "Поле для родительского класса изделия необходимо заполнить",
        )

    def test_name_is_required(self):
        """Проверяет, что поле name обязательно для заполнения."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": None,
            "short_name": None,
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["name"][0], "Поле для названия класса необходимо заполнить"
        )

    def test_short_name_is_optional_accepts_empty_string(self):
        """Проверяет, что поле short_name может быть пустой строкой и форма проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": None,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_short_name_is_optional_accepts_none(self):
        """Проверяет, что поле short_name может быть равно None и форма проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": "",
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_image_field_is_optional_accepts_none(self):
        """Проверяет, что поле image может быть равно None и форма проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_invalid_class_field_object_raises_validation_error(self):
        """Проверяет, что выбор class_field, не входящего в products(), вызывает ошибку валидации."""
        form_data = {
            "class_field": self.INVALID_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_non_jpg_or_png_image_raises_validation_error(self):
        """Проверяет, что загрузка изображения с недопустимым расширением (не jpg/png) вызывает ошибку валидации."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.GIF_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_jpg_image_is_valid(self):
        """Проверяет, что загрузка изображения .jpg проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.JPG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_png_image_is_valid(self):
        """Проверяет, что загрузка изображения .png проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_object_with_minimal_requirements_is_valid(self):
        """Проверяет, что форма с минимально необходимыми данными (class_field, name) проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": None,
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_object_with_minimal_requirements_is_saved_correctly(self):
        """Проверяет, что форма с минимальными данными корректно сохраняет объект."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": "",
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.class_field, form_data["class_field"])
        self.assertNotEqual(obj.image.name, form_files["image"])

    def test_object_with_maximum_requirements_is_valid(self):
        """Проверяет, что форма со всеми заполненными полями (включая short_name и image) проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_object_with_maximum_requirements_is_saved_correctly(self):
        """Проверяет, что форма со всеми полями корректно сохраняет объект."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.class_field, form_data["class_field"])
        self.assertNotEqual(obj.image.name, form_files["image"])

    def test_class_field_relationship(self):
        """Проверяет, что объект связывается с правильным class_field через обратную связь."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        obj = form.save()

        self.assertIn(obj, self.NUTS_CLASS.class_products.all())

    def test_edit_existing_object_updates_fields(self):
        """Проверяет, что при редактировании существующего объекта все поля обновляются корректно."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        obj = form.save()

        new_form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.NEW_PROD_NAME,
            "short_name": self.NEW_PROD_SHORT_NAME,
        }
        new_form_files = {
            "image": self.JPG_IMAGE,
        }
        form = ProdForm(data=new_form_data, files=new_form_files, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, new_form_data["name"])
        self.assertEqual(obj.short_name, new_form_data["short_name"])
        self.assertEqual(obj.class_field, new_form_data["class_field"])
        self.assertNotEqual(obj.image.name, new_form_files["image"])

    def test_edit_without_image_keeps_old_image(self):
        """Проверяет, что при редактировании без загрузки нового изображения старый файл сохраняется."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        obj = form.save()

        new_form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.NEW_PROD_NAME,
            "short_name": self.NEW_PROD_SHORT_NAME,
        }
        form = ProdForm(data=new_form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, new_form_data["name"])
        self.assertEqual(obj.short_name, new_form_data["short_name"])
        self.assertEqual(obj.class_field, new_form_data["class_field"])
        self.assertNotEqual(obj.image.name, form_files["image"])
