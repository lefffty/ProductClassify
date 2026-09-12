from django.contrib.auth.models import Group
from faker import Faker

from tests.unit.base import BaseUnitTestCase

from accounts.forms import SignUpForm
from accounts.models import User, Role
from accounts.constants import (
    UserConsts, RoleConsts
)
from accounts.errors import SignUpErrors


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
