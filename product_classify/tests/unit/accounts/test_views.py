from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth import get_user_model

from faker import Faker
from http import HTTPStatus

from tests.unit.base import BaseUnitTestCase

from accounts.constants import UserConsts
from accounts.errors import UserErrors


User = get_user_model()


class LoginViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.active_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
        )

        cls.inactive_email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.inactive_password = "StrongPass456!"
        cls.inactive_user = User.objects.create_user(
            email=cls.inactive_email,
            first_name=cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH],
            last_name=cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH],
            phone_number="+7 (111) 222-33-44",
            password=cls.inactive_password,
        )
        cls.inactive_user.is_active = False
        cls.inactive_user.save()

        cls.staff_email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.staff_password = "StrongPass789!"
        cls.staff_user = User.objects.create_user(
            email=cls.staff_email,
            first_name=cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH],
            last_name=cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH],
            phone_number="+7 (222) 333-44-55",
            password=cls.staff_password,
        )
        cls.staff_user.is_staff = True
        cls.staff_user.save()

        cls.valid_login_data = {
            "email": cls.email,
            "password": cls.password,
        }

        cls.wrong_password_data = {
            "email": cls.email,
            "password": "WrongPassword999!",
        }

        cls.unknown_email_data = {
            "email": "nonexistent@example.com",
            "password": cls.password,
        }

        cls.inactive_login_data = {
            "email": cls.inactive_email,
            "password": cls.inactive_password,
        }

        cls.empty_email_data = {
            "email": "",
            "password": cls.password,
        }

        cls.empty_password_data = {
            "email": cls.email,
            "password": "",
        }

        cls.invalid_email_data = {
            "email": "not-an-email",
            "password": cls.password,
        }

        cls.login_url = reverse("accounts:login")
        cls.index_url = reverse("classes:index")

    def test_get_returns_200_status_code(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_login_template(self):
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_renders_form_in_template(self):
        response = self.client.get(self.login_url)
        self.assertIn("form", response.context)

    def test_login_function_was_called_during_user_authentication(self):
        with patch("accounts.views.login") as mock_login:
            self.client.post(self.login_url, self.valid_login_data)
            args, _ = mock_login.call_args
            self.assertEqual(args[0].method, "POST")
            self.assertEqual(args[1], self.active_user)

    def test_successful_login_create_user_session(self):
        self.client.post(self.login_url, data={
            "email": self.email,
            "password": self.password,
        })
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(
            int(self.client.session.get("_auth_user_id")),
            self.active_user.pk,
        )

    def test_redirects_after_successful_login(self):
        response = self.client.post(self.login_url, data={
            "email": self.email,
            "password": self.password,
        })
        self.assertRedirects(response, self.index_url)

    def test_invalid_credentials_returns_200_status_code(self):
        response = self.client.post(self.login_url, data={
            **self.invalid_email_data
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.context["form"].is_valid())
        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_inactive_user_is_not_logged_in(self):
        response = self.client.post(self.login_url, data=self.inactive_login_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unknown_email_raises_invalid_credentials_error(self):
        response = self.client.post(self.login_url, self.unknown_email_data)
        self.assertContains(response, UserErrors.INVALID_CREDENTIALS)

    def test_wrong_password_raises_invalid_credentials_error(self):
        response = self.client.post(self.login_url, self.wrong_password_data)
        self.assertContains(response, UserErrors.INVALID_CREDENTIALS)

    def test_empty_email_returns_200_status_code_and_displays_invalid_credentials_error_message(self):
        response = self.client.post(self.login_url, data=self.empty_email_data)
        self.assertContains(response, UserErrors.EMPTY_EMAIL)

    def test_empty_password_returns_200_status_code_and_displays_invalid_credentials_error_message(self):
        response = self.client.post(self.login_url, data=self.empty_password_data)
        self.assertContains(response, UserErrors.EMPTY_PASSWORD)

    def test_invalid_post_validation_error_is_shown_on_page(self):
        response = self.client.post(self.login_url, data=self.wrong_password_data)
        self.assertContains(response, UserErrors.INVALID_CREDENTIALS)

    def test_authenticated_user_redirected_to_main_page(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.index_url)

    def test_password_not_in_html_response(self):
        response = self.client.post(
            self.login_url,
            data=self.valid_login_data,
            follow=True
        )
        self.assertNotContains(response, self.password)
