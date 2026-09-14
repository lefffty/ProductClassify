from django.contrib.auth import get_user_model
from django.urls import reverse

from urllib.parse import urlencode
from faker import Faker
from random import randint
from http import HTTPStatus

from tests.unit.base import BaseUnitTestCase

from accounts.models import Role
from accounts.constants import UserConsts, RoleCodes

from ei.models import Ei
from ei.errors import EiErrors
from ei.constants import EiConsts

User = get_user_model()


class EiListViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-66"

        cls.not_allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.not_allowed_role,
        )

        cls.url = reverse("ei:list")
        cls.login_url = reverse("accounts:login")

    def test_ei_list_returns_302_code_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{self.login_url}?{urlencode({"next": self.url})}"
        self.assertRedirects(response, expected_url)

    def test_returns_403_code_for_not_authorized_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_code_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_view_uses_ei_list_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/list.html")

    def test_has_eis_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("eis", response.context)

    def test_has_fastener_classes_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)


class EiDetailViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-66"

        cls.not_allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.not_allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-65"

        cls.instance = Ei.objects.first()
        cls.url = reverse("ei:detail", args=[cls.instance.pk])
        cls.login_url = reverse("accounts:login")

    def test_returns_302_code_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{self.login_url}?{urlencode({"next": self.url})}"
        self.assertRedirects(response, expected_url)

    def test_returns_403_code_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_code_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_ei_detail_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/detail.html")

    def test_has_ei_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("ei", response.context)

    def test_has_fastener_classes_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_ei_data_is_successfully_displayed_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertContains(response, self.instance.pk)
        self.assertContains(response, self.instance.name)
        self.assertContains(response, self.instance.short_name)
        self.assertContains(response, self.instance.convert_factor)


class EiCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.main_class = Ei.objects.first()

        cls.data = {
            "name": cls.faker.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": cls.faker.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            "code": cls.faker.postcode()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": randint(1, 100),
            "main_class": cls.main_class.pk,
        }
        cls.empty_name_data = {
            "name": "",
            "short_name": cls.faker.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            "code": cls.faker.postcode()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": randint(1, 100),
            "main_class": cls.main_class.pk,
        }
        cls.empty_short_name_data = {
            "name": cls.faker.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": "",
            "code": cls.faker.postcode()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": randint(1, 100),
            "main_class": cls.main_class.pk,
        }
        cls.empty_convert_factor_data = {
            "name": cls.faker.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": cls.faker.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            "code": cls.faker.postcode()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": "",
            "main_class": cls.main_class.pk,
        }
        cls.negative_convert_factor_data = {
            "name": cls.faker.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": cls.faker.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            "code": cls.faker.postcode()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": -1,
            "main_class": cls.main_class.pk,
        }

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-66"

        cls.not_allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.not_allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-65"


        cls.url = reverse("ei:add")
        cls.redirect_url = reverse("ei:list")

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

    def test_uses_detail_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/ei.html")

    def test_renders_ei_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_has_fastener_classes_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        count_before = Ei.objects.count()
        self.client.post(self.url, data=self.data)
        self.assertEqual(Ei.objects.count(), count_before + 1)

    def test_redirects_after_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_name_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.empty_name_data)
        self.assertContains(response, EiErrors.EMPTY_NAME)

    def test_empty_short_name_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)        
        response = self.client.post(self.url, data=self.empty_short_name_data)
        self.assertContains(response, EiErrors.EMPTY_SHORT_NAME)

    def test_empty_convert_factor_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.empty_convert_factor_data)
        self.assertContains(response, EiErrors.EMPTY_FACTOR)

    def test_negative_convert_factor_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.negative_convert_factor_data)
        self.assertContains(response, EiErrors.NEGATIVE_FACTOR)


class EiDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
    
        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-66"

        cls.not_allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.not_allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-65"

        cls.ei_id = Ei.objects.last().pk
        cls.url = reverse("ei:delete", args=[cls.ei_id])
        cls.redirect_url = reverse("ei:list")

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

    def test_uses_ei_detail_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/ei.html")

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        count_before = Ei.objects.count()
        self.client.post(self.url)
        self.assertEqual(Ei.objects.count(), count_before - 1)

    def test_redirects_after_successful_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class EiUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ei = Ei.objects.last()
        cls.ei_id = cls.ei.pk
        cls.faker = Faker()

        cls.data = {
            "name": cls.faker.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": cls.faker.name()[:EiConsts.SHORT_NAME_MAX_LENGTH].strip(),
            "code": cls.faker.postcode()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": randint(1, 100),
            "main_class": cls.ei.main_class.pk,
        }

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-66"

        cls.not_allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.not_allowed_role,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-65"

        cls.url = reverse("ei:edit", args=[cls.ei_id])
        cls.redirect_url = reverse("ei:detail", args=[cls.ei_id])

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

    def test_uses_ei_update_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/ei.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.data)
        ei = Ei.objects.last()
        self.assertEqual(ei.name, self.data["name"])
        self.assertEqual(ei.short_name, self.data["short_name"])
        self.assertEqual(ei.code, self.data["code"])
        self.assertEqual(ei.convert_factor, self.data["convert_factor"])
        self.assertEqual(ei.main_class.pk, self.data["main_class"])

    def test_redirect_after_successful_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.redirect_url)
