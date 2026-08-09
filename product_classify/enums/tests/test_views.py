from django.test import TestCase
from django.urls import reverse

from faker import Faker

from random import randint

from classes.models import ClassStruct
from classes.constants import (
    ENUM_CLASSES_IDS,
    CLASS_STRUCT_NAME_MAX_LENGTH,
    CLASS_STRUCT_SHORT_NAME_MAX_LENGTH
)

from enums.models import Enums


class EnumsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.int_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[-1])
        cls.string_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[0])
        cls.int_enum_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:CLASS_STRUCT_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:CLASS_STRUCT_SHORT_NAME_MAX_LENGTH],
            main_class=cls.int_enum,
            base_ei=None,
        )
        cls.enum_id1 = cls.int_enum.pk
        cls.enum_id2 = cls.string_enum.pk

        cls.url1 = reverse("enums:enums_list", kwargs={"class_id": cls.enum_id1})
        cls.url2 = reverse("enums:enums_list", kwargs={"class_id": cls.enum_id2})

        cls.enum1 = Enums.objects.create(
            enum=cls.int_enum_subclass,
            num=1,
            name=None,
            short_name=None,
            double_value=None,
            int_value=randint(1, 100),
            image=None
        )
        cls.enum2 = Enums.objects.create(
            enum=cls.int_enum_subclass,
            num=2,
            name=None,
            short_name=None,
            double_value=None,
            int_value=randint(1, 100),
            image=None
        )

    def test_enums_list_view_uses_enums_list_template(self):
        response = self.client.get(self.url1)
        self.assertTemplateUsed(response, "enums/list.html")

    def test_enums_list_view_renders_enums(self):
        response = self.client.get(self.url1)
        self.assertIn("enums", response.context)

    def test_enums_list_view_renders_correct_number_of_enums_on_page(self):
        response = self.client.get(self.url1)
        self.assertEqual(response.context["enums"].count(), 2)

    def test_enums_list_view_renders_zero_enums_if_there_is_no_enums_values_for_that_enum_type(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.context["enums"].count(), 0)
    