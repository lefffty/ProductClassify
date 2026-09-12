from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, authenticate
from django.test import RequestFactory
from django import forms

from faker import Faker

from tests.unit.base import BaseUnitTestCase

from accounts.forms import SignUpForm, LoginForm
from accounts.models import Role
from accounts.constants import (
    UserConsts, RoleConsts
)
from accounts.errors import SignUpErrors, UserErrors


User = get_user_model()


class SignUpFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        group_self = Group.objects.create(name=cls.faker.name()[:16])
        cls.self_registerable_role = Role.objects.create(
            code=cls.faker.slug()[:50],
            name=cls.faker.name()[:RoleConsts.NAME_MAX_LENGTH],
            description=cls.faker.text(),
            group=group_self,
            is_self_registerable=True,
        )

        group_not_self = Group.objects.create(name=cls.faker.name()[:16])
        cls.not_self_registerable_role = Role.objects.create(
            code=cls.faker.slug()[:50],
            name=cls.faker.name()[:RoleConsts.NAME_MAX_LENGTH],
            description=cls.faker.text(),
            group=group_not_self,
            is_self_registerable=False,
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"
        cls.password1 = "StrongPass123!"
        cls.password2 = "StrongPass123!"

        cls.valid_data = {
            "email": cls.email,
            "first_name": cls.first_name,
            "middle_name": cls.middle_name,
            "last_name": cls.last_name,
            "phone_number": cls.phone_number,
            "role": cls.self_registerable_role.pk,
            "password1": cls.password1,
            "password2": cls.password2,
        }

        cls.empty_email_data = {
            **cls.valid_data,
            "email": "",
        }
        cls.empty_first_name_data = {
            **cls.valid_data,
            "first_name": "",
        }
        cls.empty_last_name_data = {
            **cls.valid_data,
            "last_name": "",
        }
        cls.empty_phone_number_data = {
            **cls.valid_data,
            "phone_number": "",
        }
        cls.empty_role_data = {
            **cls.valid_data,
            "role": "",
        }

        cls.mismatched_passwords_data = {
            **cls.valid_data,
            "password2": "AnotherPass456!",
        }
        cls.too_short_password_data = {
            **cls.valid_data,
            "password1": "123",
            "password2": "123",
        }

        cls.existing_user = User.objects.create_user(
            email=cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH],
            first_name=cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH],
            last_name=cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH],
            phone_number="+7 (111) 222-33-44",
            password=cls.faker.password(),
        )

        cls.duplicate_email_data = {
            **cls.valid_data,
            "email": cls.existing_user.email,
            "phone_number": "+7 (999) 555-66-77",
        }
        cls.duplicate_phone_number_data = {
            **cls.valid_data,
            "email": cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH],
            "phone_number": cls.existing_user.phone_number,
        }

        cls.invalid_phone_data = {
            **cls.valid_data,
            "phone_number": "8-999-123-45-67",
        }

    def test_role_queryset_contains_only_self_registerable_roles(self):
        form = SignUpForm()
        queryset = form.fields["role"].queryset

        self.assertIn(self.self_registerable_role, queryset)
        self.assertNotIn(self.not_self_registerable_role, queryset)

    def test_valid_form_data(self):
        form = SignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_is_required(self):
        form = SignUpForm(data=self.empty_email_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_first_name_is_required(self):
        form = SignUpForm(data=self.empty_first_name_data)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    def test_last_name_is_required(self):
        form = SignUpForm(data=self.empty_last_name_data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)

    def test_phone_number_is_required(self):
        form = SignUpForm(data=self.empty_phone_number_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_role_is_required(self):
        form = SignUpForm(data=self.empty_role_data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_middle_name_is_optional(self):
        data = self.valid_data.copy()
        data["middle_name"] = ""
        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_middle_name_can_be_none(self):
        data = self.valid_data.copy()
        data.pop("middle_name", None)
        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_passwords_must_match(self):
        form = SignUpForm(data=self.mismatched_passwords_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_password_too_short(self):
        form = SignUpForm(data=self.too_short_password_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_duplicate_email_is_invalid(self):
        form = SignUpForm(data=self.duplicate_email_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_duplicate_phone_number_is_invalid(self):
        form = SignUpForm(data=self.duplicate_phone_number_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_invalid_phone_number_is_invalid(self):
        form = SignUpForm(data=self.invalid_phone_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_role_not_self_registerable_is_invalid(self):
        data = self.valid_data.copy()
        data["role"] = self.not_self_registerable_role.pk
        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_save_creates_user(self):
        form = SignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)

        self.assertIsNotNone(user.pk)
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(user.first_name, self.valid_data["first_name"])
        self.assertEqual(user.middle_name, self.valid_data["middle_name"])
        self.assertEqual(user.last_name, self.valid_data["last_name"])
        self.assertEqual(user.phone_number, self.valid_data["phone_number"])
        self.assertEqual(user.role, self.self_registerable_role)

    def test_save_hashes_password(self):
        form = SignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)

        self.assertNotEqual(user.password, self.password1)
        self.assertTrue(user.check_password(self.password1))

    def test_save_adds_user_to_role_group(self):
        form = SignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)

        self.assertIn(self.self_registerable_role.group, user.groups.all())

    def test_save_with_commit_false_raises_not_implemented(self):
        form = SignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

        with self.assertRaises(NotImplementedError) as ctx:
            form.save(commit=False)
        self.assertEqual(str(ctx.exception), SignUpErrors.COMMIT_IS_FALSE)

    def test_form_meta_model(self):
        self.assertEqual(SignUpForm._meta.model, User)

    def test_form_meta_fields(self):
        expected = (
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "phone_number",
            "role",
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
        cls.faker = Faker()
        cls.factory = RequestFactory()

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

        cls.valid_data = {
            "email": cls.email,
            "password": cls.password,
        }

        cls.empty_email_data = {
            "email": "",
            "password": cls.password,
        }
        cls.empty_password_data = {
            "email": cls.email,
            "password": "",
        }
        cls.empty_both_data = {
            "email": "",
            "password": "",
        }

        cls.wrong_password_data = {
            "email": cls.email,
            "password": "WrongPassword999!",
        }
        cls.unknown_email_data = {
            "email": "nonexistent@example.com",
            "password": cls.password,
        }

        cls.inactive_user_data = {
            "email": cls.inactive_email,
            "password": cls.inactive_password,
        }

        cls.invalid_email_data = {
            "email": "not-an-email",
            "password": cls.password,
        }

        cls.too_long_email_data = {
            "email": "a" * (UserConsts.EMAIL_MAX_LENGTH + 1) + "@example.com",
            "password": cls.password,
        }
        cls.too_long_password_data = {
            "email": cls.email,
            "password": "x" * (UserConsts.PASSWORD_MAX_LENGTH + 1),
        }

    def test_valid_form_data(self):
        form = LoginForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_authenticates_user(self):
        request = self.factory.post("/login/")
        form = LoginForm(data=self.valid_data, request=request)
        self.assertTrue(form.is_valid(), form.errors)

        user = authenticate(
            request=request,
            username=self.valid_data["email"],
            password=self.valid_data["password"],
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.active_user.pk)

    def test_form_without_request_still_valid(self):
        form = LoginForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_is_required(self):
        form = LoginForm(data=self.empty_email_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(
            form.errors["email"][0],
            UserErrors.EMPTY_EMAIL,
        )

    def test_password_is_required(self):
        form = LoginForm(data=self.empty_password_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(
            form.errors["password"][0],
            UserErrors.EMPTY_PASSWORD,
        )

    def test_empty_both_fields(self):
        form = LoginForm(data=self.empty_both_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("password", form.errors)

    def test_wrong_password_is_invalid(self):
        form = LoginForm(data=self.wrong_password_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            UserErrors.INVALID_CREDENTIALS,
            form.errors["__all__"],
        )

    def test_unknown_email_is_invalid(self):
        form = LoginForm(data=self.unknown_email_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            UserErrors.INVALID_CREDENTIALS,
            form.errors["__all__"],
        )

    def test_invalid_credentials_does_not_reveal_which_field_is_wrong(self):
        form_wrong_password = LoginForm(data=self.wrong_password_data)
        form_unknown_email = LoginForm(data=self.unknown_email_data)

        self.assertFalse(form_wrong_password.is_valid())
        self.assertFalse(form_unknown_email.is_valid())

        self.assertEqual(
            form_wrong_password.errors["__all__"][0],
            form_unknown_email.errors["__all__"][0],
        )

    def test_inactive_user_is_invalid(self):
        form = LoginForm(data=self.inactive_user_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            UserErrors.INACTIVE_USER,
        )

    def test_inactive_user_message_differs_from_invalid_credentials(self):
        form_inactive = LoginForm(data=self.inactive_user_data)
        form_wrong = LoginForm(data=self.wrong_password_data)

        self.assertNotEqual(
            form_inactive.errors["__all__"][0],
            form_wrong.errors["__all__"][0],
        )

    def test_invalid_email_format_is_invalid(self):
        form = LoginForm(data=self.invalid_email_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_too_long_email_is_invalid(self):
        form = LoginForm(data=self.too_long_email_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_too_long_password_is_invalid(self):
        form = LoginForm(data=self.too_long_password_data)
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
        form = LoginForm(data=self.empty_email_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.fields["email"].error_messages["required"],
            UserErrors.EMPTY_EMAIL,
        )

    def test_password_error_message(self):
        form = LoginForm(data=self.empty_password_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.fields["password"].error_messages["required"],
            UserErrors.EMPTY_PASSWORD,
        )

    def test_form_without_request(self):
        form = LoginForm(data=self.valid_data)
        self.assertIsNone(form.request)

    def test_clean_returns_cleaned_data(self):
        form = LoginForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], self.email)
        self.assertEqual(form.cleaned_data["password"], self.password)

    def test_clean_does_not_call_authenticate_with_empty_fields(self):
        form = LoginForm(data=self.empty_both_data)
        self.assertFalse(form.is_valid())
        self.assertNotIn("__all__", form.errors)

    def test_email_is_case_sensitive(self):
        data = {
            "email": self.email.upper(),
            "password": self.password,
        }
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn(UserErrors.INVALID_CREDENTIALS, form.errors["__all__"])
