from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError

from tests.unit.accounts.factories.user import UserFactory
from tests.unit.base import BaseUnitTestCase
from tests.unit.accounts.factories.role import RoleFactory

from accounts.models import Role

from faker import Faker


class RoleModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.group1, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])
        cls.group2, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])
        cls.group3, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])

        cls.valid_role = RoleFactory(group=cls.group1)
        cls.existing_role = RoleFactory(group=cls.group3)

    def test_valid_data(self):
        self.assertIsNotNone(self.valid_role.pk)
        self.assertTrue(self.valid_role.code)
        self.assertTrue(self.valid_role.name)
        self.assertEqual(self.valid_role.group, self.group1)

    def test_update_data_result(self):
        Role.objects.filter(pk=self.valid_role.pk).update(
            group=self.group2,
        )
        self.valid_role.refresh_from_db()
        self.assertEqual(self.valid_role.group, self.group2)

    def test_empty_code_data(self):
        role = RoleFactory.build(group=self.group1, code="")
        with self.assertRaises(ValidationError) as ctx:
            role.full_clean()
        self.assertIn("code", ctx.exception.message_dict)

    def test_empty_group_data(self):
        with self.assertRaises(IntegrityError):
            RoleFactory(group=None)

    def test_duplicate_code_data(self):
        with self.assertRaises(IntegrityError):
            RoleFactory(group=self.group2, code=self.existing_role.code)

    def test_duplicate_name_data(self):
        with self.assertRaises(IntegrityError):
            RoleFactory(group=self.group2, name=self.existing_role.name)



class UserModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.group1, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])
        cls.group2, _ = Group.objects.get_or_create(name=cls.faker.name()[:16])

        cls.role1 = RoleFactory(group=cls.group1)
        cls.role2 = RoleFactory(group=cls.group2)

        cls.password = "StrongPass123!"

        cls.existing_user = UserFactory()

    def test_create_user_successfully(self):
        user = UserFactory(role=self.role1, password=self.password)
        self.assertIsNotNone(user.pk)
        self.assertTrue(user.email)
        self.assertTrue(user.first_name)
        self.assertTrue(user.last_name)
        self.assertTrue(user.phone_number)
        self.assertEqual(user.role, self.role1)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_password_is_hashed(self):
        user = UserFactory(password=self.password)
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.check_password(self.password))

    def test_create_user_without_middle_name(self):
        user = UserFactory(middle_name=None)
        self.assertIsNone(user.middle_name)

    def test_create_user_without_role(self):
        user = UserFactory(role=None)
        self.assertIsNone(user.role)

    def test_create_superuser(self):
        user = UserFactory(is_staff=True, is_superuser=True)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str_with_middle_name(self):
        user = UserFactory.build(
            email="test@example.com",
            first_name="Иван",
            middle_name="Иванович",
            last_name="Иванов",
            phone_number="+7 (999) 123-45-67",
        )
        self.assertEqual(str(user), "test@example.com - Иванов И.И.")

    def test_user_str_without_middle_name(self):
        user = UserFactory.build(
            email="test@example.com",
            first_name="Иван",
            middle_name=None,
            last_name="Иванов",
            phone_number="+7 (999) 123-45-67",
        )
        self.assertEqual(str(user), "test@example.com - Иванов И.")

    def test_save_sets_group_from_role(self):
        user = UserFactory(role=self.role1)
        self.assertIn(self.role1.group, user.groups.all())

    def test_save_updates_group_when_role_changes(self):
        user = UserFactory(role=self.role1)
        self.assertIn(self.role1.group, user.groups.all())

        user.role = self.role2
        user.save()
        user.refresh_from_db()

        self.assertNotIn(self.role1.group, user.groups.all())
        self.assertIn(self.role2.group, user.groups.all())

    def test_save_without_role_does_not_set_groups(self):
        user = UserFactory(role=None)
        self.assertEqual(user.groups.count(), 0)

    def test_email_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            UserFactory(email=self.existing_user.email)

    def test_phone_number_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            UserFactory(phone_number=self.existing_user.phone_number)

    def test_empty_email_raises_validation_error(self):
        user = UserFactory.build(email="", role=self.role1)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("email", ctx.exception.message_dict)

    def test_empty_first_name_raises_validation_error(self):
        user = UserFactory.build(first_name="", role=self.role1)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("first_name", ctx.exception.message_dict)

    def test_empty_last_name_raises_validation_error(self):
        user = UserFactory.build(last_name="", role=self.role1)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("last_name", ctx.exception.message_dict)

    def test_empty_phone_number_raises_validation_error(self):
        user = UserFactory.build(phone_number="", role=self.role1)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("phone_number", ctx.exception.message_dict)

    def test_invalid_phone_number_raises_validation_error(self):
        user = UserFactory.build(
            phone_number="8-999-123-45-67",
            role=self.role1,
        )
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
            user = UserFactory.build(phone_number=number)
            try:
                user.full_clean(exclude=["role"])
            except ValidationError:
                self.fail(f"Номер {number} должен быть валидным")

    def test_role_on_delete_protect(self):
        UserFactory(role=self.role1)
        with self.assertRaises(ProtectedError):
            self.role1.delete()
