from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError

from tests.unit.base import BaseUnitTestCase

from accounts.constants import RoleConsts, UserConsts
from accounts.models import Role, User

from faker import Faker


class RoleModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        group1_name = cls.faker.name()[:16]
        cls.group1, _ = Group.objects.get_or_create(name=group1_name)

        group2_name = cls.faker.name()[:16]
        cls.group2, _ = Group.objects.get_or_create(name=group2_name)

        group3_name = cls.faker.name()[:16]
        cls.group3, _ = Group.objects.get_or_create(name=group3_name)

        cls.code = cls.faker.slug()[:50]
        cls.name = cls.faker.name()[:RoleConsts.NAME_MAX_LENGTH]
        cls.description = cls.faker.text()
        cls.is_self_registerable = cls.faker.boolean()

        cls.valid_data = {
            "code": cls.code,
            "name": cls.name,
            "description": cls.description,
            "group": cls.group1,
            "is_self_registerable": cls.is_self_registerable,
        }

        cls.new_code = cls.faker.slug()[:50]
        cls.new_name = cls.faker.name()[:RoleConsts.NAME_MAX_LENGTH]
        cls.new_description = cls.faker.text()
        cls.new_is_self_registerable = not cls.is_self_registerable

        cls.update_data = {
            "code": cls.new_code,
            "name": cls.new_name,
            "description": cls.new_description,
            "group": cls.group2,
            "is_self_registerable": cls.new_is_self_registerable,
        }

        cls.empty_code_data = {
            "code": "",
            "name": cls.name,
            "description": cls.description,
            "group": cls.group1,
            "is_self_registerable": cls.is_self_registerable,
        }

        cls.empty_name_data = {
            "code": cls.code,
            "name": "",
            "description": cls.description,
            "group": cls.group1,
            "is_self_registerable": cls.is_self_registerable,
        }

        cls.empty_group_data = {
            "code": cls.code,
            "name": cls.name,
            "description": cls.description,
            "group": None,
            "is_self_registerable": cls.is_self_registerable,
        }

        cls.existing_role = Role.objects.create(
            code=cls.faker.slug()[:50],
            name=cls.faker.name()[:RoleConsts.NAME_MAX_LENGTH],
            description=cls.faker.text(),
            group=cls.group3,
            is_self_registerable=cls.faker.boolean(),
        )

        cls.duplicate_code_data = {
            "code": cls.existing_role.code,
            "name": cls.faker.name()[:RoleConsts.NAME_MAX_LENGTH],
            "description": cls.faker.text(),
            "group": cls.group2,
            "is_self_registerable": cls.faker.boolean(),
        }

        cls.duplicate_name_data = {
            "code": cls.faker.slug()[:50],
            "name": cls.existing_role.name,
            "description": cls.faker.text(),
            "group": cls.group2,
            "is_self_registerable": cls.faker.boolean(),
        }

    def test_valid_data(self):
        role = Role.objects.create(
            **self.valid_data
        )
        self.assertEqual(Role.objects.count(), 11)
        self.assertIsNotNone(role.pk)
        self.assertEqual(role.name, self.valid_data["name"])
        self.assertEqual(role.code, self.valid_data["code"])
        self.assertEqual(role.description, self.valid_data["description"])
        self.assertEqual(role.is_self_registerable, self.valid_data["is_self_registerable"])
        self.assertEqual(role.group, self.valid_data["group"])

    def test_update_data_result(self):
        role = Role.objects.create(
            **self.valid_data
        )
        Role.objects.filter(pk=role.pk).update(
            **self.update_data
        )
        role.refresh_from_db()
        self.assertEqual(role.name, self.update_data["name"])
        self.assertEqual(role.code, self.update_data["code"])
        self.assertEqual(role.description, self.update_data["description"])
        self.assertEqual(role.is_self_registerable, self.update_data["is_self_registerable"])
        self.assertEqual(role.group, self.update_data["group"])

    def test_empty_code_data(self):
        role = Role.objects.create(
            **self.empty_code_data
        )
        with self.assertRaises(ValidationError) as ctx:
            role.full_clean()
        self.assertIn("code", ctx.exception.message_dict)

    def test_empty_group_data(self):
        with self.assertRaises(IntegrityError):
            Role.objects.create(
                **self.empty_group_data
            )

    def test_duplicate_code_data(self):        
        with self.assertRaises(IntegrityError):
            Role.objects.create(
                **self.duplicate_code_data
            )

    def test_duplicate_name_data(self):
        with self.assertRaises(IntegrityError):
            Role.objects.create(
                **self.duplicate_name_data
            )


class UserModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        group1 = Group.objects.create(name=cls.faker.name()[:16])
        cls.role1 = Role.objects.create(
            code=cls.faker.slug()[:50],
            name=cls.faker.name()[:RoleConsts.NAME_MAX_LENGTH],
            description=cls.faker.text(),
            group=group1,
            is_self_registerable=cls.faker.boolean(),
        )

        group2 = Group.objects.create(name=cls.faker.name()[:16])
        cls.role2 = Role.objects.create(
            code=cls.faker.slug()[:50],
            name=cls.faker.name()[:RoleConsts.NAME_MAX_LENGTH],
            description=cls.faker.text(),
            group=group2,
            is_self_registerable=cls.faker.boolean(),
        )

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"
        cls.password = cls.faker.password()

        cls.valid_data = {
            "email": cls.email,
            "first_name": cls.first_name,
            "middle_name": cls.middle_name,
            "last_name": cls.last_name,
            "phone_number": cls.phone_number,
            "password": cls.password,
            "role": cls.role1,
        }

        cls.new_email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.new_first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.new_middle_name = cls.faker.name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.new_last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.new_phone_number = "+7 (495) 765-43-21"

        cls.update_data = {
            "email": cls.new_email,
            "first_name": cls.new_first_name,
            "middle_name": cls.new_middle_name,
            "last_name": cls.new_last_name,
            "phone_number": cls.new_phone_number,
            "role": cls.role2,
        }

        cls.empty_email_data = {
            "email": "",
            "first_name": cls.first_name,
            "middle_name": cls.middle_name,
            "last_name": cls.last_name,
            "phone_number": cls.phone_number,
            "password": cls.password,
        }

        cls.empty_first_name_data = {
            "email": cls.email,
            "first_name": "",
            "middle_name": cls.middle_name,
            "last_name": cls.last_name,
            "phone_number": cls.phone_number,
            "password": cls.password,
        }

        cls.empty_last_name_data = {
            "email": cls.email,
            "first_name": cls.first_name,
            "middle_name": cls.middle_name,
            "last_name": "",
            "phone_number": cls.phone_number,
            "password": cls.password,
        }

        cls.empty_phone_number_data = {
            "email": cls.email,
            "first_name": cls.first_name,
            "middle_name": cls.middle_name,
            "last_name": cls.last_name,
            "phone_number": "",
            "password": cls.password,
        }

        cls.none_middle_name_data = {
            "email": cls.email,
            "first_name": cls.first_name,
            "middle_name": None,
            "last_name": cls.last_name,
            "phone_number": cls.phone_number,
            "password": cls.password,
        }

        cls.invalid_phone_number_data = {
            "email": cls.email,
            "first_name": cls.first_name,
            "middle_name": cls.middle_name,
            "last_name": cls.last_name,
            "phone_number": "8-999-123-45-67", 
            "password": cls.password,
        }

        cls.existing_user = User.objects.create_user(
            email=cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH],
            first_name=cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH],
            last_name=cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH],
            phone_number="+7 (111) 222-33-44",
            password=cls.faker.password(),
        )

        cls.duplicate_email_data = {
            "email": cls.existing_user.email,
            "first_name": cls.first_name,
            "middle_name": cls.middle_name,
            "last_name": cls.last_name,
            "phone_number": cls.phone_number,
            "password": cls.password,
        }

        cls.duplicate_phone_number_data = {
            "email": cls.email,
            "first_name": cls.first_name,
            "middle_name": cls.middle_name,
            "last_name": cls.last_name,
            "phone_number": cls.existing_user.phone_number,
            "password": cls.password,
        }

    def test_create_user_successfully(self):
        user = User.objects.create_user(**self.valid_data)
        self.assertIsNotNone(user.pk)
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(user.first_name, self.valid_data["first_name"])
        self.assertEqual(user.middle_name, self.valid_data["middle_name"])
        self.assertEqual(user.last_name, self.valid_data["last_name"])
        self.assertEqual(user.phone_number, self.valid_data["phone_number"])
        self.assertEqual(user.role, self.role1)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_password_is_hashed(self):
        user = User.objects.create_user(**self.valid_data)
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.check_password(self.password))

    def test_create_user_without_middle_name(self):
        data = self.valid_data.copy()
        data["middle_name"] = None
        user = User.objects.create_user(**data)
        self.assertIsNone(user.middle_name)

    def test_create_user_without_role(self):
        data = self.valid_data.copy()
        data["role"] = None
        user = User.objects.create_user(**data)
        self.assertIsNone(user.role)

    def test_create_superuser(self):
        email = self.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        user = User.objects.create_superuser(
            email=email,
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number="+7 (999) 000-11-22",
            password=self.password,
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str_with_middle_name(self):
        user = User(
            email="test@example.com",
            first_name="Иван",
            middle_name="Иванович",
            last_name="Иванов",
            phone_number="+7 (999) 123-45-67",
        )
        self.assertEqual(str(user), "test@example.com - Иванов И.И.")

    def test_user_str_without_middle_name(self):
        user = User(
            email="test@example.com",
            first_name="Иван",
            middle_name=None,
            last_name="Иванов",
            phone_number="+7 (999) 123-45-67",
        )
        self.assertEqual(str(user), "test@example.com - Иванов И.")

    def test_save_sets_group_from_role(self):
        user = User.objects.create_user(**self.valid_data)
        self.assertIn(self.role1.group, user.groups.all())

    def test_save_updates_group_when_role_changes(self):
        user = User.objects.create_user(**self.valid_data)
        self.assertIn(self.role1.group, user.groups.all())

        user.role = self.role2
        user.save()
        user.refresh_from_db()

        self.assertNotIn(self.role1.group, user.groups.all())
        self.assertIn(self.role2.group, user.groups.all())

    def test_save_without_role_does_not_set_groups(self):
        data = self.valid_data.copy()
        data["role"] = None
        user = User.objects.create_user(**data)
        self.assertEqual(user.groups.count(), 0)

    def test_email_must_be_unique(self):
        data = self.valid_data.copy()
        data["email"] = self.existing_user.email
        data["phone_number"] = "+7 (999) 555-66-77"
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**data)

    def test_phone_number_must_be_unique(self):
        data = self.valid_data.copy()
        data["phone_number"] = self.existing_user.phone_number
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**data)

    def test_empty_email_raises_validation_error(self):
        data = self.valid_data.copy()
        data["email"] = ""
        user = User(**data)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("email", ctx.exception.message_dict)

    def test_empty_first_name_raises_validation_error(self):
        data = self.valid_data.copy()
        data["first_name"] = ""
        user = User(**data)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("first_name", ctx.exception.message_dict)

    def test_empty_last_name_raises_validation_error(self):
        data = self.valid_data.copy()
        data["last_name"] = ""
        user = User(**data)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("last_name", ctx.exception.message_dict)

    def test_empty_phone_number_raises_validation_error(self):
        data = self.valid_data.copy()
        data["phone_number"] = ""
        user = User(**data)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("phone_number", ctx.exception.message_dict)

    def test_invalid_phone_number_raises_validation_error(self):
        data = self.valid_data.copy()
        data["phone_number"] = "8-999-123-45-67"
        user = User(**data)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("phone_number", ctx.exception.message_dict)

    def test_valid_phone_number_formats(self):
        valid_numbers = [
            "+7 (999) 123-45-67",
            "+7 (495) 000-00-00",
            "+7 (111) 111-11-11",
        ]
        for number in valid_numbers:
            data = self.valid_data.copy()
            data["email"] = self.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
            data["phone_number"] = number
            user = User(**data)
            try:
                user.full_clean(exclude=["role"])  # role может быть занята
            except ValidationError:
                self.fail(f"Номер {number} должен быть валидным")

    def test_role_on_delete_protect(self):
        User.objects.create_user(**self.valid_data)
        with self.assertRaises(ProtectedError):
            self.role1.delete()
