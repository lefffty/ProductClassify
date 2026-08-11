from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker
from random import randint
from io import BytesIO
from PIL import Image

from classes.models import ClassStruct
from classes.constants import (
    ENUM_CLASSES_IDS,
    CLASS_STRUCT_NAME_MAX_LENGTH,
    CLASS_STRUCT_SHORT_NAME_MAX_LENGTH
)

from enums.constants import (
    ENUMS_FORM_NAME_MAX_LENGTH,
    ENUMS_FORM_SHORT_NAME_MAX_LENGTH
)
from enums.constants import (
    EMPTY_ENUM_ERROR,
    EMPTY_INT_ENUM_FIELDS_ERROR,
    NEGATIVE_INT_VALUE_ERROR,
    WRONG_FIELDS_INT_ENUM_WAS_SPECIFIED_ERROR,
    EMPTY_DOUBLE_ENUM_FIELDS_ERROR,
    NEGATIVE_DOUBLE_VALUE_ERROR,
    WRONG_FIELDS_DOUBLE_ENUM_WAS_SPECIFIED_ERROR,
    EMPTY_STRING_ENUM_FIELDS_ERROR,
    WRONG_FIELDS_STRING_ENUM_WAS_SPECIFIED_ERROR,
    EMPTY_IMAGE_ENUM_FIELDS_ERROR,
    WRONG_FIELDS_IMAGE_ENUM_WAS_SPECIFIED_ERROR
)
from enums.models import Enums


class EnumsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.int_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[-1])
        cls.string_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[0])
        cls.int_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.int_enum,
            base_ei=None,
        )
        cls.enum_id1 = cls.int_enum.pk
        cls.enum_id2 = cls.string_enum.pk

        cls.url1 = reverse("enums:enums_list", kwargs={"class_id": cls.enum_id1})
        cls.url2 = reverse("enums:enums_list", kwargs={"class_id": cls.enum_id2})

        cls.enum1 = Enums.objects.create(
            enum=cls.int_enum_subclass,
            num=1,
            name=None,
            short_name=None,
            double_value=None,
            int_value=randint(1, 100),
            image=None
        )
        cls.enum2 = Enums.objects.create(
            enum=cls.int_enum_subclass,
            num=2,
            name=None,
            short_name=None,
            double_value=None,
            int_value=randint(1, 100),
            image=None
        )

    def test_enums_list_view_uses_enums_list_template(self):
        response = self.client.get(self.url1)
        self.assertTemplateUsed(response, "enums/list.html")

    def test_enums_list_view_renders_enums(self):
        response = self.client.get(self.url1)
        self.assertIn("enums", response.context)

    def test_enums_list_view_renders_correct_number_of_enums_on_page(self):
        response = self.client.get(self.url1)
        self.assertEqual(response.context["enums"].count(), 2)

    def test_enums_list_view_renders_zero_enums_if_there_is_no_enums_values_for_that_enum_type(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.context["enums"].count(), 0)


class EnumsDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.int_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[-1])
        cls.int_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.int_enum,
            base_ei=None,
        )
        cls.enum = Enums.objects.create(
            enum=cls.int_enum_subclass,
            num=1,
            name=None,
            short_name=None,
            double_value=None,
            int_value=randint(1, 100),
            image=None
        )
        cls.url = reverse("enums:enums_detail", args=[cls.int_enum_subclass.pk, cls.enum.pk])

    def test_enums_detail_view_uses_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "enums/detail.html")

    def test_enums_detail_views_has_enum_object_is_context(self):
        response = self.client.get(self.url)
        self.assertIn("enum", response.context)

    def test_enums_detail_views_has_enum_value_is_context(self):
        response = self.client.get(self.url)
        self.assertIn("enum_value", response.context)

    def test_enums_detail_views_correctly_renders_information_about_enum(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.enum.enum.name)
        self.assertContains(response, self.enum.value)


class EnumsCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.int_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[-1])
        cls.string_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[0])
        cls.image_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[1])
        cls.double_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[2])

        cls.int_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.int_enum,
            base_ei=None,
        )
        cls.string_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.string_enum,
            base_ei=None,
        )
        cls.image_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.image_enum,
            base_ei=None,
        )
        cls.double_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.double_enum,
            base_ei=None,
        )

        cls.url = reverse("enums:add_enum")
        cls.redirect_url = reverse("classes:index")

        cls.int_enum_valid_data = {
            "enum": cls.int_enum_subclass.pk,
            "name": "",
            "short_name": "",
            "int_value": randint(1, 100),
            "double_value": "",
        }
        cls.int_enum_empty_enum_data = {
            "enum": "",
            "name": "",
            "short_name": "",
            "int_value": randint(1, 100),
            "double_value": "",
        }
        cls.int_enum_empty_int_value_data = {
            "enum": cls.int_enum_subclass.pk,
            "name": "",
            "short_name": "",
            "int_value": "",
            "double_value": "",     
        }
        cls.int_enum_negative_value_field_data = {
            "enum": cls.int_enum_subclass.pk,
            "name": "",
            "short_name": "",
            "int_value": -randint(1, 100),
            "double_value": "",
        }
        cls.int_enum_invalid_data = {
            "enum": cls.int_enum_subclass.pk,
            "name": cls.fake.name()[:ENUMS_FORM_NAME_MAX_LENGTH],
            "short_name": "",
            "int_value": randint(1, 100),
            "double_value": "",
        }

        cls.string_enum_empty_fields_data = {
            "enum": cls.string_enum_subclass.pk,
            "name": cls.fake.name()[:ENUMS_FORM_NAME_MAX_LENGTH],
            "short_name": "",
            "int_value": "",
            "double_value": "",
        }
        cls.string_enum_invalid_data = {
            "enum": cls.string_enum_subclass.pk,
            "name": cls.fake.name()[:ENUMS_FORM_NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:ENUMS_FORM_SHORT_NAME_MAX_LENGTH],
            "int_value": randint(1, 100),
            "double_value": "",
        }

        cls.image = cls._create_test_image()
        cls.image_enum_empty_fields_data = {
            "enum": cls.image_enum_subclass.pk,
            "name": "",
            "short_name": "",
            "int_value": "",
            "double_value": "",
        }
        cls.image_enum_invalid_data = {
            "enum": cls.image_enum_subclass.pk,
            "name": "",
            "short_name": "",
            "int_value": randint(1, 100),
            "double_value": "",
            "image": cls.image,
        }

        cls.double_enum_empty_fields_data = {
            "enum": cls.double_enum_subclass.pk,
            "name": "",
            "short_name": "",
            "int_value": "",
            "double_value": "",
        }
        cls.double_enum_negative_value_data = {
            "enum": cls.double_enum_subclass.pk,
            "name": "",
            "short_name": "",
            "int_value": "",
            "double_value": -randint(1, 100),
        }
        cls.double_enum_invalid_data = {
            "enum": cls.double_enum_subclass.pk,
            "name": cls.fake.name()[:ENUMS_FORM_NAME_MAX_LENGTH],
            "short_name": "",
            "int_value": "",
            "double_value": randint(1, 100),
        }

    def _create_test_image(extension='jpg'):
        image = Image.new('RGB', (100, 100), color='red')
        file = BytesIO()
        format = 'JPEG' if extension == 'jpg' else 'PNG'
        image.save(file, format=format)
        file.seek(0)
        return SimpleUploadedFile(
            f"test.{extension}",
            file.read(),
            content_type=f"image/{extension if extension != 'jpg' else 'jpeg'}"
        )

    def test_enums_create_view_uses_enum_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "enums/enum.html")

    def test_enums_create_view_renders_create_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_enums_create_view_can_save_a_POST_request(self):
        count_before = Enums.objects.count()
        self.client.post(
            path=self.url,
            data=self.int_enum_valid_data,
        )
        self.assertEqual(Enums.objects.count(), count_before + 1)
        last = Enums.objects.last()
        self.assertEqual(self.int_enum_valid_data["enum"], last.enum.pk)
        self.assertEqual(self.int_enum_valid_data["int_value"], last.int_value)

    def test_enums_create_view_redirect_after_successful_POST_request(self):
        response = self.client.post(
            path=self.url,
            data=self.int_enum_valid_data,
        )
        self.assertRedirects(response, self.redirect_url)

    def test_enums_create_view_shows_validation_error_on_page_if_enum_field_was_not_specified(self):
        response = self.client.post(
            path=self.url,
            data=self.int_enum_empty_enum_data
        )
        self.assertContains(response, escape(EMPTY_ENUM_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_name_or_short_name_fields_was_not_specified_for_string_enum(self):
        response = self.client.post(
            path=self.url,
            data=self.string_enum_empty_fields_data
        )
        self.assertContains(response, escape(EMPTY_STRING_ENUM_FIELDS_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_int_value_or_double_value_or_image_fields_was_specified_for_string_enum(self):
        response = self.client.post(
            path=self.url,
            data=self.string_enum_invalid_data
        )
        self.assertContains(response, escape(WRONG_FIELDS_STRING_ENUM_WAS_SPECIFIED_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_image_field_was_not_specified_for_image_enum(self):
        response = self.client.post(
            path=self.url,
            data=self.image_enum_empty_fields_data
        )
        self.assertContains(response, escape(EMPTY_IMAGE_ENUM_FIELDS_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_int_value_or_double_value_fields_was_specified_for_image_enum(self):
        response = self.client.post(
            path=self.url,
            data=self.image_enum_invalid_data,
        )
        self.assertContains(response, escape(WRONG_FIELDS_IMAGE_ENUM_WAS_SPECIFIED_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_double_value_field_was_not_specified_for_double_enum(self):
        response = self.client.post(
            path=self.url,
            data=self.double_enum_empty_fields_data
        )
        self.assertContains(response, escape(EMPTY_DOUBLE_ENUM_FIELDS_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_double_value_is_negative(self):
        response = self.client.post(
            path=self.url,
            data=self.double_enum_negative_value_data
        )
        self.assertContains(response, escape(NEGATIVE_DOUBLE_VALUE_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_int_value_or_image_or_name_or_short_name_fields_was_specified_for_double_enum(self):
        response = self.client.post(
            path=self.url,
            data=self.double_enum_invalid_data
        )
        self.assertContains(response, escape(WRONG_FIELDS_DOUBLE_ENUM_WAS_SPECIFIED_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_int_value_was_not_specified_for_int_enum(self):
        response = self.client.post(
            path=self.url,
            data=self.int_enum_empty_int_value_data,
        )
        self.assertContains(response, escape(EMPTY_INT_ENUM_FIELDS_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_int_value_is_negative(self):
        response = self.client.post(
            path=self.url,
            data=self.int_enum_negative_value_field_data
        )
        self.assertContains(response, escape(NEGATIVE_INT_VALUE_ERROR))

    def test_enums_create_view_shows_validation_error_on_page_if_double_value_or_image_or_name_or_short_name_field_was_specified_for_int_enum(self):
        response = self.client.post(
            path=self.url,
            data=self.int_enum_invalid_data
        )
        self.assertContains(response, escape(WRONG_FIELDS_INT_ENUM_WAS_SPECIFIED_ERROR))


class EnumsDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.int_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[-1])

        cls.int_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.int_enum,
            base_ei=None,
        )

        cls.int_enum_instance = Enums.objects.create(
            name=None,
            num=1,
            short_name=None,
            enum=cls.int_enum,
            int_value=randint(1, 100),
            double_value=None,
            image=None,
        )

        cls.url = reverse("enums:delete_enum", kwargs={"enum_id": cls.int_enum_instance.pk, "class_id": cls.int_enum_subclass.pk})
        cls.redirect_url = reverse("enums:enums_list", kwargs={"class_id": cls.int_enum.pk})

    def test_enums_delete_view_uses_enum_template(self):
        response = self.client.get(
            path=self.url,
        )
        self.assertTemplateUsed(response, "enums/enum.html")

    def test_enums_delete_view_renders_enum_instance(self):
        response = self.client.get(
            path=self.url
        )
        self.assertIn("instance", response.context)

    def test_enums_delete_view_can_save_a_POST_request(self):
        count_before = Enums.objects.count()
        self.client.post(
            path=self.url
        )
        self.assertEqual(Enums.objects.count(), count_before - 1)

    def test_enums_delete_view_redirects_after_successful_POST_request(self):
        response = self.client.post(
            path=self.url,
        )
        self.assertRedirects(response, self.redirect_url)


class EnumsUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.int_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[-1])
        cls.int_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.int_enum,
            base_ei=None,
        )

        cls.instance = Enums.objects.create(
            name=None,
            num=1,
            short_name=None,
            enum=cls.int_enum_subclass,
            int_value=randint(1, 100),
            double_value=None,
            image=None,
        )

        cls.url = reverse("enums:edit_enum", kwargs={
            "class_id": cls.instance.enum.pk,
            "enum_id": cls.instance.pk
        })
        cls.redirect_url = reverse("enums:enums_detail", kwargs={
            "class_id": cls.instance.enum.pk,
            "enum_id": cls.instance.pk,
        })

        cls.update_data = {
            "name": "",
            "short_name": "",
            "enum": cls.int_enum_subclass.pk,
            "int_value": randint(1, 100),
            "double_value": "",
            "image": "",
        }

    def test_enums_update_view_uses_enum_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "enums/enum.html")

    def test_enums_update_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_enums_update_view_has_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_enums_update_view_can_save_a_POST_request(self):
        response = self.client.post(self.url, data=self.update_data)
        if response.status_code == 200:
            print(response.context["form"].errors)
        enum = Enums.objects.last()
        self.assertEqual(enum.int_value, self.update_data["int_value"])
        self.assertEqual(enum.enum.pk, self.update_data["enum"])

    def test_enums_update_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.update_data)
        self.assertRedirects(response, self.redirect_url)
