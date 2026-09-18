from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from django.test import RequestFactory
from django import forms
from faker import Faker


from tests.unit.accounts.factories.login import LoginFormData
from tests.unit.accounts.factories.role import RoleFactory
from tests.unit.accounts.factories.signup import SignUpFormData
from tests.unit.accounts.factories.user import UserFactory
from tests.unit.base import BaseUnitTestCase

from accounts.forms import SignUpForm, LoginForm
from accounts.constants import (
    UserConsts
)
from accounts.errors import SignUpErrors, UserErrors


User = get_user_model()


class SignUpFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.group1, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])
        cls.group2, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])
    
        cls.self_registerable_role = RoleFactory(is_self_registerable=True, group=cls.group1)
        cls.not_self_registerable_role = RoleFactory(is_self_registerable=False, group=cls.group2)

        cls.password1 = "StrongPass123!"
        cls.password2 = "StrongPass123!"

        cls.existing_user = UserFactory()

    def _valid_data(self, **overrides):
        data = SignUpFormData(
            role=self.self_registerable_role.pk,
            password1=self.password1,
            password2=self.password2,
        )
        data.update(overrides)
        return data

    def test_role_queryset_contains_only_self_registerable_roles(self):
        form = SignUpForm()
        queryset = form.fields["role"].queryset
        self.assertIn(self.self_registerable_role, queryset)
        self.assertNotIn(self.not_self_registerable_role, queryset)

    def test_valid_form_data(self):
        form = SignUpForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_is_required(self):
        form = SignUpForm(data=self._valid_data(email=""))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_first_name_is_required(self):
        form = SignUpForm(data=self._valid_data(first_name=""))
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    def test_last_name_is_required(self):
        form = SignUpForm(data=self._valid_data(last_name=""))
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)

    def test_phone_number_is_required(self):
        form = SignUpForm(data=self._valid_data(phone_number=""))
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_role_is_required(self):
        form = SignUpForm(data=self._valid_data(role=""))
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_middle_name_is_optional(self):
        form = SignUpForm(data=self._valid_data(middle_name=""))
        self.assertTrue(form.is_valid(), form.errors)

    def test_middle_name_can_be_none(self):
        data = self._valid_data()
        data.pop("middle_name", None)
        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_passwords_must_match(self):
        form = SignUpForm(
            data=self._valid_data(password2="AnotherPass456!")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_password_too_short(self):
        form = SignUpForm(
            data=self._valid_data(password1="123", password2="123")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_duplicate_email_is_invalid(self):
        form = SignUpForm(
            data=self._valid_data(email=self.existing_user.email)
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_duplicate_phone_number_is_invalid(self):
        form = SignUpForm(
            data=self._valid_data(phone_number=self.existing_user.phone_number)
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_invalid_phone_number_is_invalid(self):
        form = SignUpForm(
            data=self._valid_data(phone_number="8-999-123-45-67")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_role_not_self_registerable_is_invalid(self):
        form = SignUpForm(
            data=self._valid_data(role=self.not_self_registerable_role.pk)
        )
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_save_creates_user(self):
        data = self._valid_data()
        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)

        self.assertIsNotNone(user.pk)
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.middle_name, data["middle_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.phone_number, data["phone_number"])
        self.assertEqual(user.role, self.self_registerable_role)

    def test_save_hashes_password(self):
        form = SignUpForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)

        self.assertNotEqual(user.password, self.password1)
        self.assertTrue(user.check_password(self.password1))

    def test_save_adds_user_to_role_group(self):
        form = SignUpForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)

        self.assertIn(self.self_registerable_role.group, user.groups.all())

    def test_save_with_commit_false_raises_not_implemented(self):
        form = SignUpForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

        with self.assertRaises(NotImplementedError) as ctx:
            form.save(commit=False)
        self.assertEqual(str(ctx.exception), SignUpErrors.COMMIT_IS_FALSE)

    def test_form_meta_model(self):
        self.assertEqual(SignUpForm._meta.model, User)

    def test_form_meta_fields(self):
        expected = (
            "email", "first_name", "middle_name",
            "last_name", "phone_number", "role",
        )
        self.assertEqual(SignUpForm._meta.fields, expected)

    def test_role_field_label_and_empty_label(self):
        form = SignUpForm()
        self.assertEqual(form.fields["role"].label, "Роль")
        self.assertEqual(form.fields["role"].empty_label, "Выберите роль")
        self.assertTrue(form.fields["role"].required)


class LoginFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

        cls.password = "StrongPass123!"
        cls.active_user = UserFactory(password=cls.password)

        cls.inactive_password = "StrongPass456!"
        cls.inactive_user = UserFactory(
            is_active=False,
            password=cls.inactive_password,
        )

    def _data(self, **overrides):
        data = LoginFormData(
            email=self.active_user.email,
            password=self.password,
        )
        data.update(overrides)
        return data

    def test_valid_form_data(self):
        form = LoginForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_authenticates_user(self):
        request = self.factory.post("/login/")
        form = LoginForm(data=self._data(), request=request)
        self.assertTrue(form.is_valid(), form.errors)

        user = authenticate(
            request=request,
            username=self.active_user.email,
            password=self.password,
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.active_user.pk)

    def test_form_without_request_still_valid(self):
        form = LoginForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_is_required(self):
        form = LoginForm(data=self._data(email=""))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(form.errors["email"][0], UserErrors.EMPTY_EMAIL)

    def test_password_is_required(self):
        form = LoginForm(data=self._data(password=""))
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], UserErrors.EMPTY_PASSWORD)

    def test_empty_both_fields(self):
        form = LoginForm(data=self._data(email="", password=""))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("password", form.errors)

    def test_wrong_password_is_invalid(self):
        form = LoginForm(data=self._data(password="WrongPassword999!"))
        self.assertFalse(form.is_valid())
        self.assertIn(UserErrors.INVALID_CREDENTIALS, form.errors["__all__"])

    def test_unknown_email_is_invalid(self):
        form = LoginForm(data=self._data(email="nonexistent@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn(UserErrors.INVALID_CREDENTIALS, form.errors["__all__"])

    def test_invalid_credentials_does_not_reveal_which_field_is_wrong(self):
        form_wrong_password = LoginForm(data=self._data(password="WrongPassword999!"))
        form_unknown_email = LoginForm(data=self._data(email="nonexistent@example.com"))

        self.assertFalse(form_wrong_password.is_valid())
        self.assertFalse(form_unknown_email.is_valid())

        self.assertEqual(
            form_wrong_password.errors["__all__"][0],
            form_unknown_email.errors["__all__"][0],
        )

    def test_inactive_user_is_invalid(self):
        form = LoginForm(data=LoginFormData(
            email=self.inactive_user.email,
            password=self.inactive_password,
        ))
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"][0], UserErrors.INACTIVE_USER)

    def test_inactive_user_message_differs_from_invalid_credentials(self):
        form_inactive = LoginForm(data=LoginFormData(
            email=self.inactive_user.email,
            password=self.inactive_password,
        ))
        form_wrong = LoginForm(data=self._data(password="WrongPassword999!"))

        self.assertNotEqual(
            form_inactive.errors["__all__"][0],
            form_wrong.errors["__all__"][0],
        )

    def test_invalid_email_format_is_invalid(self):
        form = LoginForm(data=self._data(email="not-an-email"))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_too_long_email_is_invalid(self):
        form = LoginForm(data=self._data(
            email="a" * (UserConsts.EMAIL_MAX_LENGTH + 1) + "@example.com",
        ))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_too_long_password_is_invalid(self):
        form = LoginForm(data=self._data(
            password="x" * (UserConsts.PASSWORD_MAX_LENGTH + 1),
        ))
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_email_field_metadata(self):
        form = LoginForm()
        field = form.fields["email"]

        self.assertEqual(field.label, "Адрес электронной почты")
        self.assertEqual(field.help_text, "Введите адрес электронной почты")
        self.assertEqual(field.max_length, UserConsts.EMAIL_MAX_LENGTH)
        self.assertTrue(field.required)
        self.assertIsInstance(field.widget, forms.EmailInput)
        self.assertEqual(field.widget.attrs.get("class"), "form-control")
        self.assertEqual(field.widget.attrs.get("autocomplete"), "email")
        self.assertEqual(field.widget.attrs.get("placeholder"), "you@example.com")

    def test_password_field_metadata(self):
        form = LoginForm()
        field = form.fields["password"]

        self.assertEqual(field.label, "Пароль")
        self.assertEqual(field.help_text, "Введите пароль")
        self.assertEqual(field.max_length, UserConsts.PASSWORD_MAX_LENGTH)
        self.assertTrue(field.required)
        self.assertIsInstance(field.widget, forms.PasswordInput)
        self.assertEqual(field.widget.attrs.get("class"), "form-control")
        self.assertEqual(field.widget.attrs.get("autocomplete"), "current-password")

    def test_email_error_message(self):
        form = LoginForm(data=self._data(email=""))
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.fields["email"].error_messages["required"],
            UserErrors.EMPTY_EMAIL,
        )

    def test_password_error_message(self):
        form = LoginForm(data=self._data(password=""))
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.fields["password"].error_messages["required"],
            UserErrors.EMPTY_PASSWORD,
        )

    def test_form_without_request(self):
        form = LoginForm(data=self._data())
        self.assertIsNone(form.request)

    def test_clean_returns_cleaned_data(self):
        form = LoginForm(data=self._data())
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], self.active_user.email)
        self.assertEqual(form.cleaned_data["password"], self.password)

    def test_clean_does_not_call_authenticate_with_empty_fields(self):
        form = LoginForm(data=self._data(email="", password=""))
        self.assertFalse(form.is_valid())
        self.assertNotIn("__all__", form.errors)

    def test_email_is_case_sensitive(self):
        form = LoginForm(data=self._data(email=self.active_user.email.upper()))
        self.assertFalse(form.is_valid())
        self.assertIn(UserErrors.INVALID_CREDENTIALS, form.errors["__all__"])
