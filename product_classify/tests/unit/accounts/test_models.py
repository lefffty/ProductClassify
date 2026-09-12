from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from tests.unit.base import BaseUnitTestCase

from accounts.constants import RoleConsts
from accounts.models import Role

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
