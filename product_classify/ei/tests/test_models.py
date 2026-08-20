from django.test import TestCase

from faker import Faker
from random import randint

from ei.constants import EiConsts
from ei.models import Ei


class EiModelTest(TestCase):
    def test_string_representation(self):
        ei = Ei(
            name="test_name",
            short_name="test_short_name",
            code="test_code",
            convert_factor=1,
            main_class=None,
        )
        msg = "Incorrect string representation of Ei object"
        self.assertEqual(str(ei), "test_short_name", msg)

    def test_create_with_minimal_requirements(self):
        ei = Ei.objects.create(
            name="test_name",
            short_name="test",
        )
        self.assertEqual(ei.name, "test_name")
        self.assertEqual(ei.short_name, "test")
        self.assertIsNotNone(ei.pk)
        self.assertIsNotNone(ei.code)
        self.assertIsNone(ei.convert_factor)
        self.assertIsNone(ei.main_class)

    def test_convert_factor_accepts_integer(self):
        ei = Ei.objects.create(name="test_name", short_name="test", convert_factor=1)
        self.assertEqual(ei.convert_factor, 1)

    def test_convert_factor_accepts_float(self):
        ei = Ei.objects.create(name="test_name", short_name="test", convert_factor=1.0)
        self.assertEqual(ei.convert_factor, 1.0)

    def test_main_class_relation(self):
        parent = Ei.objects.create(
            name="parent",
            short_name="parent",
        )
        child = Ei.objects.create(name="child", short_name="child", main_class=parent)
        self.assertEqual(child.main_class, parent)
        self.assertIn(child, parent.child_eis.all())

    def test_main_class_reassignment_is_correct_(self):
        fake = Faker()
        ei1 = Ei.objects.create(
            name=fake.name()[:EiConsts.NAME_MAX_LENGTH],
            short_name=fake.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            code=fake.name()[:EiConsts.CODE_MAX_LENGTH],
            convert_factor=1,
            main_class=None
        )
        ei2 = Ei.objects.create(
            name=fake.name()[:EiConsts.NAME_MAX_LENGTH],
            short_name=fake.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            code=fake.name()[:EiConsts.CODE_MAX_LENGTH],
            convert_factor=randint(2, 100),
            main_class=ei1
        )
        ei3 = Ei.objects.create(
            name=fake.name()[:EiConsts.NAME_MAX_LENGTH],
            short_name=fake.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            code=fake.name()[:EiConsts.CODE_MAX_LENGTH],
            convert_factor=randint(2, 100),
            main_class=ei1
        )

        ei1.delete()
        ei2.refresh_from_db()
        ei3.refresh_from_db()
        self.assertNotEqual(ei2.main_class, ei1)
        self.assertIsNone(ei2.main_class)
        self.assertEqual(ei3.main_class, ei2)
