from django.urls import reverse
from django.utils.html import escape
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from urllib.parse import urlencode
from http import HTTPStatus
from io import BytesIO
from PIL import Image

from tests.unit.base import BaseUnitTestCase
from tests.unit.accounts.factories.user import UserFactory
from tests.unit.classes.factories.class_struct import ClassStructFactory
from tests.unit.enums.factories.enums import EnumsFactory, EnumsFormData, ChangeNumFormData

from accounts.models import Role
from accounts.constants import RoleCodes

from classes.models import ClassStruct
from classes.constants import EnumsIds

from enums.errors import (
    StringEnumErrors,
    CommonEnumErrors, 
    ImageEnumErrors, 
    IntEnumErrors, 
    DoubleEnumErrors, 
    ChangeNumErrors
)
from enums.models import Enums

User = get_user_model()


class EnumsListViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.string_enum = ClassStruct.objects.get(pk=EnumsIds.STRING)

        cls.int_enum_subclass = ClassStructFactory(
            main_class=cls.int_enum,
        )

        cls.enum_id1 = cls.int_enum.pk
        cls.enum_id2 = cls.string_enum.pk

        cls.enum1 = EnumsFactory(
            enum=cls.int_enum_subclass,
            num=1,
            int_value=42,
        )
        cls.enum2 = EnumsFactory(
            enum=cls.int_enum_subclass,
            num=2,
            int_value=7,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.login_url = reverse("accounts:login")
        cls.url1 = reverse("enums:list", kwargs={"class_id": cls.enum_id1})
        cls.url2 = reverse("enums:list", kwargs={"class_id": cls.enum_id2})

    def test_returns_302_code_for_anonymous_user(self):
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{self.login_url}?{urlencode({"next": self.url1})}"
        self.assertRedirects(response, expected_url)

    def test_returns_403_code_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_code_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_enums_list_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url1)
        self.assertTemplateUsed(response, "enums/list.html")

    def test_renders_enums(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url1)
        self.assertIn("enums", response.context)

    def test_renders_correct_number_of_enums_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url1)
        self.assertEqual(response.context["enums"].count(), 2)

    def test_renders_zero_enums_if_there_is_no_enums_values_for_that_enum_type(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url2)
        self.assertEqual(response.context["enums"].count(), 0)


class EnumsDetailViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)

        cls.int_enum_subclass = ClassStructFactory(
            main_class=cls.int_enum,
        )
        cls.enum = EnumsFactory(
            enum=cls.int_enum_subclass,
            num=1,
            int_value=42,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.login_url = reverse("accounts:login")
        cls.url = reverse("enums:detail", args=[cls.int_enum_subclass.pk, cls.enum.pk])

    def test_returns_302_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{self.login_url}?{urlencode({"next": self.url})}"
        self.assertRedirects(response, expected_url)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_detail_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "enums/detail.html")

    def test_has_enum_object_is_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("enum", response.context)

    def test_correctly_renders_information_about_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertContains(response, self.enum.enum.name)
        self.assertContains(response, self.enum.value)


class EnumsCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.string_enum = ClassStruct.objects.get(pk=EnumsIds.STRING)
        cls.image_enum = ClassStruct.objects.get(pk=EnumsIds.IMAGE)
        cls.double_enum = ClassStruct.objects.get(pk=EnumsIds.DOUBLE)

        cls.int_enum_subclass = ClassStructFactory(main_class=cls.int_enum)
        cls.string_enum_subclass = ClassStructFactory(main_class=cls.string_enum)
        cls.image_enum_subclass = ClassStructFactory(main_class=cls.image_enum)
        cls.double_enum_subclass = ClassStructFactory(main_class=cls.double_enum)

        cls.int_enum_valid_data = EnumsFormData(
            enum=cls.int_enum_subclass.pk,
            name="",
            short_name="",
            int_value=42,
            double_value="",
            image="",
        )
        cls.int_enum_empty_enum_data = EnumsFormData(
            enum="",
            name="",
            short_name="",
            int_value=42,
            double_value="",
            image="",
        )
        cls.int_enum_empty_int_value_data = EnumsFormData(
            enum=cls.int_enum_subclass.pk,
            name="",
            short_name="",
            int_value="",
            double_value="",
            image="",
        )
        cls.int_enum_negative_value_field_data = EnumsFormData(
            enum=cls.int_enum_subclass.pk,
            name="",
            short_name="",
            int_value=-42,
            double_value="",
            image="",
        )
        cls.int_enum_invalid_data = EnumsFormData(
            enum=cls.int_enum_subclass.pk,
            name="Test name",
            short_name="",
            int_value=42,
            double_value="",
            image="",
        )

        cls.string_enum_empty_fields_data = EnumsFormData(
            enum=cls.string_enum_subclass.pk,
            name="Test short",
            short_name="",
            int_value="",
            double_value="",
            image="",
        )
        cls.string_enum_invalid_data = EnumsFormData(
            enum=cls.string_enum_subclass.pk,
            name="Test name",
            short_name="Test short",
            int_value=42,
            double_value="",
            image="",
        )

        cls.image = cls._create_test_image()
        cls.image_enum_empty_fields_data = EnumsFormData(
            enum=cls.image_enum_subclass.pk,
            name="",
            short_name="",
            int_value="",
            double_value="",
            image="",
        )
        cls.image_enum_invalid_data = EnumsFormData(
            enum=cls.image_enum_subclass.pk,
            name="",
            short_name="",
            int_value=42,
            double_value="",
            image=cls.image,
        )

        cls.double_enum_empty_fields_data = EnumsFormData(
            enum=cls.double_enum_subclass.pk,
            name="",
            short_name="",
            int_value="",
            image="",
            double_value="",
        )
        cls.double_enum_negative_value_data = EnumsFormData(
            enum=cls.double_enum_subclass.pk,
            name="",
            short_name="",
            int_value="",
            double_value=-42.0,
            image="",
        )
        cls.double_enum_invalid_data = EnumsFormData(
            enum=cls.double_enum_subclass.pk,
            name="Test name",
            short_name="",
            int_value="",
            double_value=42.0,
            image="",
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("enums:add")
        cls.login_url = reverse("accounts:login")
        cls.redirect_url = reverse("classes:index")

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

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_enum_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "enums/enum.html")

    def test_renders_create_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        count_before = Enums.objects.count()
        self.client.post(
            path=self.url,
            data=self.int_enum_valid_data,
        )
        self.assertEqual(Enums.objects.count(), count_before + 1)
        last = Enums.objects.last()
        self.assertEqual(self.int_enum_valid_data["enum"], last.enum.pk)
        self.assertEqual(self.int_enum_valid_data["int_value"], last.int_value)

    def test_redirect_after_successful_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.int_enum_valid_data,
        )
        self.assertRedirects(response, self.redirect_url)

    def test_shows_validation_error_on_page_if_enum_field_was_not_specified(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.int_enum_empty_enum_data
        )
        self.assertContains(response, escape(CommonEnumErrors.EMPTY_ENUM_ERROR))

    def test_shows_validation_error_on_page_if_name_or_short_name_fields_was_not_specified_for_string_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.string_enum_empty_fields_data
        )
        self.assertContains(response, escape(StringEnumErrors.EMPTY_FIELDS_ERROR))

    def test_shows_validation_error_on_page_if_int_value_or_double_value_or_image_fields_was_specified_for_string_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.string_enum_invalid_data
        )
        self.assertContains(response, escape(StringEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR))

    def test_shows_validation_error_on_page_if_image_field_was_not_specified_for_image_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.image_enum_empty_fields_data
        )
        self.assertContains(response, escape(ImageEnumErrors.EMPTY_FIELDS_ERROR))

    def test_shows_validation_error_on_page_if_int_value_or_double_value_fields_was_specified_for_image_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.image_enum_invalid_data,
        )
        self.assertContains(response, escape(ImageEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR))

    def test_shows_validation_error_on_page_if_double_value_field_was_not_specified_for_double_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.double_enum_empty_fields_data
        )
        self.assertContains(response, escape(DoubleEnumErrors.EMPTY_FIELDS_ERROR))

    def test_shows_validation_error_on_page_if_double_value_is_negative(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.double_enum_negative_value_data
        )
        self.assertContains(response, escape(DoubleEnumErrors.NEGATIVE_VALUE_ERROR))

    def test_shows_validation_error_on_page_if_int_value_or_image_or_name_or_short_name_fields_was_specified_for_double_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.double_enum_invalid_data
        )
        self.assertContains(response, escape(DoubleEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR))

    def test_shows_validation_error_on_page_if_int_value_was_not_specified_for_int_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.int_enum_empty_int_value_data,
        )
        self.assertContains(response, escape(IntEnumErrors.EMPTY_FIELDS_ERROR))

    def test_shows_validation_error_on_page_if_int_value_is_negative(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.int_enum_negative_value_field_data
        )
        self.assertContains(response, escape(IntEnumErrors.NEGATIVE_VALUE_ERROR))

    def test_shows_validation_error_on_page_if_double_value_or_image_or_name_or_short_name_field_was_specified_for_int_enum(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.int_enum_invalid_data
        )
        self.assertContains(response, escape(IntEnumErrors.WRONG_FIELDS_WAS_SPECIFIED_ERROR))


class EnumsDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)

        cls.int_enum_subclass = ClassStructFactory(main_class=cls.int_enum)

        cls.int_enum_instance = EnumsFactory(
            enum=cls.int_enum,
            num=1,
            int_value=42,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.login_url = reverse("accounts:login")
        cls.url = reverse(
            "enums:delete",
            kwargs={
                "enum_id": cls.int_enum_instance.pk,
                "class_id": cls.int_enum_subclass.pk,
            },
        )
        cls.redirect_url = reverse("enums:list", kwargs={"class_id": cls.int_enum.pk})

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_enums_delete_view_uses_enum_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(
            path=self.url,
        )
        self.assertTemplateUsed(response, "enums/enum.html")

    def test_enums_delete_view_renders_enum_instance(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(
            path=self.url
        )
        self.assertIn("instance", response.context)

    def test_enums_delete_view_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        count_before = Enums.objects.count()
        self.client.post(
            path=self.url
        )
        self.assertEqual(Enums.objects.count(), count_before - 1)

    def test_enums_delete_view_redirects_after_successful_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
        )
        self.assertRedirects(response, self.redirect_url)


class EnumsUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)

        cls.int_enum_subclass = ClassStructFactory(main_class=cls.int_enum)

        cls.instance = EnumsFactory(
            enum=cls.int_enum_subclass,
            num=1,
            int_value=42,
        )

        cls.update_data = EnumsFormData(
            name="",
            short_name="",
            enum=cls.int_enum_subclass.pk,
            int_value=99,
            double_value="",
            image="",
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("enums:edit", kwargs={
            "class_id": cls.instance.enum.pk,
            "enum_id": cls.instance.pk,
        })
        cls.redirect_url = reverse("enums:detail", kwargs={
            "class_id": cls.instance.enum.pk,
            "enum_id": cls.instance.pk,
        })

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_enum_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "enums/enum.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_has_instance_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.update_data)
        enum = Enums.objects.last()
        self.assertEqual(enum.int_value, self.update_data["int_value"])
        self.assertEqual(enum.enum.pk, self.update_data["enum"])

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.update_data)
        self.assertRedirects(response, self.redirect_url)


class ChangeNumViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.string_enum = ClassStruct.objects.get(pk=EnumsIds.STRING)

        cls.int_enum_subclass = ClassStructFactory(main_class=cls.int_enum)
        cls.string_enum_subclass = ClassStructFactory(main_class=cls.string_enum)

        cls.instance1 = EnumsFactory(
            enum=cls.int_enum_subclass,
            num=1,
            int_value=42,
        )
        cls.instance2 = EnumsFactory(
            enum=cls.int_enum_subclass,
            num=2,
            int_value=7,
        )
        cls.instance3 = EnumsFactory(
            enum=cls.string_enum_subclass,
            num=1,
            name="String value",
            short_name="StrVal",
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.valid_data = ChangeNumFormData(
            enum_1=cls.instance1.pk,
            enum_2=cls.instance2.pk,
        )
        cls.empty_first_num_data = ChangeNumFormData(
            enum_1="",
            enum_2=cls.instance2.pk,
        )
        cls.empty_second_num_data = ChangeNumFormData(
            enum_1=cls.instance1.pk,
            enum_2="",
        )
        cls.equal_nums_data = ChangeNumFormData(
            enum_1=cls.instance1.pk,
            enum_2=cls.instance1.pk,
        )
        cls.non_same_class_data = ChangeNumFormData(
            enum_1=cls.instance1.pk,
            enum_2=cls.instance3.pk,
        )

        cls.url = reverse("enums:change_num")
        cls.redirect_url = reverse("classes:index")

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_change_num_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "enums/change_num.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_has_fastener_classes_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.valid_data)
        self.instance1.refresh_from_db()
        self.instance2.refresh_from_db()
        self.assertEqual(self.instance1.num, 2)
        self.assertEqual(self.instance2.num, 1)

    def test_redirect_after_successful_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_first_num_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.empty_first_num_data)
        self.assertContains(response, escape(ChangeNumErrors.EMPTY_FIRST_NUM))

    def test_empty_second_num_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.empty_second_num_data)
        self.assertContains(response, escape(ChangeNumErrors.EMPTY_SECOND_NUM))

    def test_equal_nums_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.equal_nums_data)
        self.assertContains(response, escape(ChangeNumErrors.EQUAL_ENUMS))

    def test_non_same_class_nums_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.non_same_class_data)
        self.assertContains(response, escape(ChangeNumErrors.NON_SAME_CLASS))
