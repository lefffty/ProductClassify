from django.http import HttpRequest
from django.contrib.auth.models import Group
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from urllib.parse import urlencode
from unittest.mock import patch
from http import HTTPStatus

from faker import Faker

from tests.unit.accounts.factories.login import LoginFormData
from tests.unit.accounts.factories.role import RoleFactory
from tests.unit.accounts.factories.signup import SignUpFormData
from tests.unit.accounts.factories.user import UserFactory, UserFormData
from tests.unit.base import BaseUnitTestCase

from accounts.errors import UserErrors, SignUpErrors

User = get_user_model()


class LoginViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "StrongPass123!"
        cls.active_user = UserFactory(password=cls.password)

        cls.inactive_password = "StrongPass456!"
        cls.inactive_user = UserFactory(
            is_active=False,
            password=cls.inactive_password,
        )

        cls.staff_password = "StrongPass789!"
        cls.staff_user = UserFactory(
            is_staff=True,
            password=cls.staff_password,
        )

        cls.valid_login_data = LoginFormData(
            email=cls.active_user.email,
            password=cls.password,
        )
        cls.wrong_password_data = LoginFormData(
            email=cls.active_user.email,
            password="WrongPassword999!",
        )
        cls.unknown_email_data = LoginFormData(
            email="nonexistent@example.com",
            password=cls.password,
        )
        cls.inactive_login_data = LoginFormData(
            email=cls.inactive_user.email,
            password=cls.inactive_password,
        )
        cls.empty_email_data = LoginFormData(
            email="",
            password=cls.password,
        )
        cls.empty_password_data = LoginFormData(
            email=cls.active_user.email,
            password="",
        )
        cls.invalid_email_data = LoginFormData(
            email="not-an-email",
            password=cls.password,
        )

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
        self.client.post(self.login_url, data=self.valid_login_data)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(
            int(self.client.session.get("_auth_user_id")),
            self.active_user.pk,
        )

    def test_redirects_after_successful_login(self):
        response = self.client.post(self.login_url, data=self.valid_login_data)
        self.assertRedirects(response, self.index_url)

    def test_invalid_credentials_returns_200_status_code(self):
        response = self.client.post(self.login_url, data=self.invalid_email_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.context["form"].is_valid())
        self.assertNotIn("_auth_user_id", self.client.session)

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
            follow=True,
        )
        self.assertNotContains(response, self.password)


class LogoutViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_user = UserFactory()

        cls.logout_url = reverse("accounts:logout")
        cls.next_url = reverse("classes:index")
        cls.index_url = reverse("classes:index")
        cls.invalid_next_url = "https://rutube.ru/"
        cls.login_url = settings.LOGIN_URL

    def test_returns_OK_status_code(self):
        self.client.force_login(self.active_user)
        response = self.client.post(self.logout_url, data={"next": self.next_url})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_uses_logout_template(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.logout_url)
        self.assertTemplateUsed(response, "accounts/logout.html")

    def test_removes_user_id_from_session(self):
        self.client.force_login(self.active_user)
        self.client.post(self.logout_url, data={"next": self.next_url})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_redirects_to_next_url_if_next_url_is_correct(self):
        self.client.force_login(self.active_user)
        response = self.client.post(self.logout_url, data={"next": self.next_url})
        self.assertRedirects(response, self.next_url, fetch_redirect_response=False)

    def test_redirects_to_main_page_if_next_url_is_incorrect(self):
        self.client.force_login(self.active_user)
        response = self.client.post(self.logout_url, data={"next": self.invalid_next_url})
        self.assertRedirects(response, self.index_url, fetch_redirect_response=False)

    def test_redirects_to_main_page_if_next_url_was_not_provided(self):
        self.client.force_login(self.active_user)
        response = self.client.post(self.logout_url, data={"next": ""})
        self.assertRedirects(response, self.index_url, fetch_redirect_response=False)

    def test_function_was_called(self):
        self.client.force_login(self.active_user)
        with patch("accounts.views.logout") as mock_logout:
            self.client.post(self.logout_url)
            mock_logout.assert_called_once()
            args, _ = mock_logout.call_args
            self.assertIsInstance(args[0], HttpRequest)

    def test_unauthorized_user_redirected_to_login_page(self):
        response = self.client.post(self.logout_url)
        self.assertIn(self.login_url, response.url)


class SignUpViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.group1, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])

        cls.self_registerable_role = RoleFactory(is_self_registerable=True, group=cls.group1)
        cls.active_user = UserFactory()

        cls.password1 = "StrongPass123!"
        cls.password2 = "StrongPass123!"

        cls.valid_data = SignUpFormData(
            role=cls.self_registerable_role.pk,
            password1=cls.password1,
            password2=cls.password2,
        )
        cls.invalid_email_data = SignUpFormData(
            email=cls.active_user.email,
            role=cls.self_registerable_role.pk,
            password1=cls.password1,
            password2=cls.password2,
        )
        cls.invalid_phone_number_data = SignUpFormData(
            phone_number=cls.active_user.phone_number,
            role=cls.self_registerable_role.pk,
            password1=cls.password1,
            password2=cls.password2,
        )

        cls.signup_url = reverse("accounts:signup")
        cls.index_url = reverse("classes:index")

    def test_signup_uses_signup_template(self):
        response = self.client.get(self.signup_url)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_signup_returns_200_status_code(self):
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_signup_redirects_to_main_page_if_user_is_authenticated(self):
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertRedirects(response, self.index_url)

    def test_signup_successfully_creates_new_user(self):
        self.client.post(self.signup_url, self.valid_data)
        self.assertEqual(User.objects.count(), 2)

    def test_user_added_to_role_group(self):
        self.client.post(self.signup_url, self.valid_data)
        user = User.objects.get(email=self.valid_data["email"])
        self.assertIn(self.self_registerable_role.group, user.groups.all())

    def test_successful_login_create_user_session(self):
        self.client.post(self.signup_url, self.valid_data)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_function_was_called(self):
        with patch("accounts.views.login") as mock_login:
            self.client.post(self.signup_url, self.valid_data)
            args, _ = mock_login.call_args
            request, user = args
            self.assertEqual(request.method, "POST")
            self.assertIsInstance(request, HttpRequest)
            self.assertEqual(user.email, self.valid_data["email"])

    def test_signup_redirects_to_main_page_for_successfully_signed_up_user(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.signup_url)
        self.assertRedirects(response, self.index_url)

    def test_non_unique_email_validation_error_is_shown_on_page(self):
        response = self.client.post(self.signup_url, self.invalid_email_data)
        self.assertContains(response, SignUpErrors.NON_UNIQUE_EMAIL)

    def test_non_unique_phone_number_validation_error_is_shown_on_page(self):
        response = self.client.post(self.signup_url, self.invalid_phone_number_data)
        self.assertContains(response, SignUpErrors.NON_UNIQUE_PHONE_NUMBER)


class ProfileViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.group1, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])
        
        cls.self_registerable_role = RoleFactory(is_self_registerable=True, group=cls.group1)
        cls.active_user = UserFactory(
            role=cls.self_registerable_role,
            middle_name="Иванович",
        )

        cls.url = reverse("accounts:profile")
        cls.login_url = reverse("accounts:login")

    def test_uses_profile_template(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_has_user_in_context(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.url)
        self.assertIn("user", response.context)

    def test_profile_returns_200_status_code(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects_anonymous_user_to_index_page_when_trying_to_access_profile_page(self):
        response = self.client.get(self.url)
        expected_url = f"{self.login_url}?{urlencode({'next': self.url})}"
        self.assertRedirects(response, expected_url)

    def test_correctly_shows_all_information_about_user(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.url)
        self.assertContains(response, self.active_user.email)
        self.assertContains(response, self.active_user.first_name)
        self.assertContains(response, self.active_user.middle_name)
        self.assertContains(response, self.active_user.last_name)
        self.assertContains(response, self.active_user.phone_number)
        self.assertContains(response, self.active_user.role)
        self.assertContains(
            response,
            "Активен" if self.active_user.is_active else "Не активен",
        )


class ProfileEditViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.group1, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])
        
        cls.self_registerable_role = RoleFactory(is_self_registerable=True, group=cls.group1)
        cls.active_user = UserFactory(
            role=cls.self_registerable_role,
            middle_name="Иванович",
        )

        cls.new_middle_name = "Петрович"
        cls.data = UserFormData(
            email=cls.active_user.email,
            first_name=cls.active_user.first_name,
            middle_name=cls.new_middle_name,
            last_name=cls.active_user.last_name,
            phone_number=cls.active_user.phone_number,
        )

        cls.url = reverse("accounts:profile_edit")
        cls.profile_url = reverse("accounts:profile")

    def test_returns_302_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_has_edit_mode_is_true_in_context(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.url)
        self.assertIn("edit_mode", response.context)
        self.assertTrue(response.context["edit_mode"])

    def test_uses_profile_template(self):
        self.client.force_login(self.active_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.active_user)
        self.client.post(self.url, data=self.data)
        self.active_user.refresh_from_db()
        self.assertEqual(self.active_user.middle_name, self.new_middle_name)

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.active_user)
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.profile_url)
