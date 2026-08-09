from django.test import TestCase
from django.utils.html import escape
from django.urls import reverse

from http import HTTPStatus
from parameterized import parameterized
from faker import Faker

from ei.models import Ei
from ei.constants import KILOGRAM_ID

from classes.models import ClassStruct
from classes.forms import ProdClassForm, EnumClassForm
from classes.constants import EMPTY_MAIN_CLASS_ERROR, EMPTY_NAME_ERROR, CLASSIFICATOR_CYCLE_ERROR
from classes.constants import (
    NUTS_ID,
    ENUM_CLASSES_IDS,
    PROD_CLASS_FORM_MAX_LENGTH,
    PROD_CLASS_FORM_SHORT_NAME_MAX_LENGTH,
    ENUM_CLASS_FORM_NAME_MAX_LENGTH,
    ENUM_CLASS_FORM_SHORT_NAME_MAX_LENGTH
)


class MainPageTemplateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reversed_url = reverse("classes:index")

    def test_main_page_template_view_uses_index_template(self):
        response = self.client.get(self.reversed_url)
        self.assertTemplateUsed(response, "classes/index.html")

    def test_fastener_classes_are_in_context(self):
        response = self.client.get(self.reversed_url)
        self.assertIn("fastener_classes", response.context)

    def test_fastener_classes_count_is_correct(self):
        response = self.client.get(self.reversed_url)
        self.assertEqual(len(response.context["fastener_classes"]), 3)

    def test_renders_nav_bar(self):
        response = self.client.get(self.reversed_url)
        self.assertContains(response, '<nav id="menu">')


class CategoryClassesListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        nuts_class = ClassStruct.objects.get(pk=3)

        ClassStruct.objects.create(
            name="Nuts subclass",
            short_name="subclass",
            main_class=nuts_class,
            base_ei=None,
        )

    @parameterized.expand([
        (3,),
        (4,),
        (5,),
    ])
    def test_category_classes_view_returns_ok_status_code(self, class_id):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.expand([
        (3,),
        (4,),
        (5,),
    ])
    def test_category_classes_view_uses_category_template(self, class_id):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertTemplateUsed(response, "classes/category.html")

    @parameterized.expand([
        (3, 1),
        (4, 0),
        (5, 0),
    ])
    def test_category_classes_view_displays_correct_number_of_subclasses(self, class_id, expected_count):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertEqual(len(response.context["classes"]), expected_count)

    def test_category_classes_view_returns_not_found_error_if_given_class_id_is_invalid(self):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 6}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        
    def test_fastener_classes_are_in_context(self):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 3}))
        self.assertIn("fastener_classes", response.context)

    def test_main_class_in_context(self):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 3}))
        self.assertIn("main_class", response.context)


class ProdClassCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nuts_class = ClassStruct.objects.get(pk=NUTS_ID)
        cls.fake = Faker()
        cls.url = reverse("classes:add_prod_class")
        cls.redirect_url = reverse("classes:index")

        cls.data = {
            "name": cls.fake.name()[:PROD_CLASS_FORM_MAX_LENGTH],
            "short_name": cls.fake.name()[:PROD_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            "base_ei": "",
            "main_class": cls.nuts_class.pk,
        }
        cls.invalid_data = {
            "name": cls.fake.name(),
            "short_name": "",
            "base_ei": "",
            "main_class": "",
        }

    def test_prod_class_create_view_uses_prod_class_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_prod_class_create_view_renders_create_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=self.url,
            data=self.data
        )
        new_class = ClassStruct.objects.last()
        self.assertEqual(ClassStruct.objects.count(), count_before + 1)
        self.assertEqual(new_class.name, self.data["name"])
        self.assertEqual(new_class.short_name, self.data["short_name"])
        self.assertIsNone(new_class.base_ei)

    def test_redirects_after_POST(self):
        response = self.client.post(
            path=self.url,
            data=self.data
        )
        self.assertRedirects(response, self.redirect_url)

    def test_for_invalid_input_renders_prod_class_template(self):
        response = self.client.post(
            path=self.url,
            data=self.invalid_data,
        )
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_invalid_prod_class_data_is_not_saved(self):
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=self.url,
            data=self.invalid_data
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)

    def test_empty_main_class_validation_error_is_shown_on_page(self):
        response = self.client.post(
            path=self.url,
            data={
                "name": self.fake.name(),
                "short_name": "",
                "base_ei": "",
                "main_class": "",
            }
        )
        self.assertContains(response, escape(EMPTY_MAIN_CLASS_ERROR))

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(
            path=self.url,
            data={
                "name": "",
                "short_name": "",
                "base_ei": "",
                "main_class": self.nuts_class.pk,
            }
        )
        self.assertContains(response, escape(EMPTY_NAME_ERROR))



class EnumClassCreateViewTest(TestCase):    
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("classes:add_enum_class")
        cls.redirect_url = reverse("classes:index")
        cls.fake = Faker()
        cls.int_enum = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[0])

        cls.valid_data = {
            "name": cls.fake.name()[:ENUM_CLASS_FORM_NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:ENUM_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            "base_ei": "",
            "main_class": cls.int_enum.pk,
        }
        cls.invalid_data = {
            "name": "",
            "short_name": "",
            "base_ei": "",
            "main_class": "",
        }

    def test_enum_class_create_view_uses_enum_class_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_enum_class_create_view_render_enum_class_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_enum_class_create_view_can_save_a_POST_request(self):
        count_before = ClassStruct.objects.count()
        response = self.client.post(
            path=self.url,
            data=self.valid_data
        )
        if response.status_code == HTTPStatus.OK:
            print(response.context["form"].errors)
        new_enum_class = ClassStruct.objects.last()
        self.assertEqual(ClassStruct.objects.count(), count_before + 1)
        self.assertEqual(new_enum_class.name, self.valid_data["name"])
        self.assertEqual(new_enum_class.short_name, self.valid_data["short_name"])
        self.assertEqual(new_enum_class.main_class.pk, self.valid_data["main_class"])
        self.assertIsNone(new_enum_class.base_ei)

    def test_enum_class_create_view_redirect_after_correct_POST_request(self):
        response = self.client.post(
            path=self.url,
            data=self.valid_data
        )
        self.assertRedirects(response, self.redirect_url)

    def test_enum_class_create_view_renders_enum_class_template_for_invalid_input(self):
        response = self.client.post(
            path=self.url,
            data=self.invalid_data
        )
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(
            path=self.url,
            data={
                "name": "",
                "short_name": "",
                "main_class": self.int_enum.pk,
                "base_ei": ""
            }
        )
        self.assertContains(response, escape(EMPTY_NAME_ERROR))

    def test_empty_main_class_validation_error_is_shown_on_page(self):
        response = self.client.post(
            path=self.url,
            data={
                "name": self.fake.name(),
                "short_name": "",
                "main_class": "",
                "base_ei": ""
            }
        )
        self.assertContains(response, escape(EMPTY_MAIN_CLASS_ERROR))


class ClassUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum_class = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[0])
        cls.nuts_class = ClassStruct.objects.get(pk=NUTS_ID)
        cls.base_ei = Ei.objects.get(pk=KILOGRAM_ID)
        cls.fake = Faker()

        cls.enum_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ENUM_CLASS_FORM_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ENUM_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.int_enum_class,
        )
        cls.support_enum_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ENUM_CLASS_FORM_NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ENUM_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.enum_class,
        )
        cls.enum_class_edit_data = {
            "name": cls.fake.name()[:ENUM_CLASS_FORM_NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:ENUM_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            "base_ei": "",
            "main_class": cls.int_enum_class.pk,
        }
        cls.invalid_enum_class_edit_data = {
            "name": cls.fake.name()[:ENUM_CLASS_FORM_NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:ENUM_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            "base_ei": "",
            "main_class": cls.enum_class.pk,
        }
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:PROD_CLASS_FORM_MAX_LENGTH],
            short_name=cls.fake.name()[:PROD_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.support_prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:PROD_CLASS_FORM_MAX_LENGTH],
            short_name=cls.fake.name()[:PROD_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.prod_class,
        )
        cls.prod_class_edit_data = {
            "name": cls.fake.name()[:PROD_CLASS_FORM_MAX_LENGTH],
            "short_name": cls.fake.name()[:PROD_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            "base_ei": cls.base_ei.pk,
            "main_class": cls.nuts_class.pk,
        }
        cls.invalid_prod_class_edit_data = {
            "name": cls.fake.name()[:PROD_CLASS_FORM_MAX_LENGTH],
            "short_name": cls.fake.name()[:PROD_CLASS_FORM_SHORT_NAME_MAX_LENGTH],
            "base_ei": cls.base_ei.pk,
            "main_class": cls.prod_class.pk,
        }

    def test_class_update_view_uses_enum_class_template_for_enum_class(self):
        response = self.client.get(
            path=reverse("classes:edit_class", args=[self.enum_class.pk]),
        )
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_class_update_view_uses_prod_class_template_for_prod_class(self):
        response = self.client.get(
            path=reverse("classes:edit_class", args=[self.prod_class.pk]),
        )
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_class_update_view_renders_enum_class_form_for_enum_class(self):
        response = self.client.get(
            path=reverse("classes:edit_class", args=[self.enum_class.pk]),
        )
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], EnumClassForm)

    def test_class_update_view_renders_prod_class_form_for_prod_class(self):
        response = self.client.get(
            path=reverse("classes:edit_class", args=[self.prod_class.pk]),
        )
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], ProdClassForm)

    def test_class_update_view_can_save_a_POST_request_for_prod_class(self):
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=reverse("classes:edit_class", args=[self.prod_class.pk]),
            data=self.prod_class_edit_data
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)
        updated_instance = ClassStruct.objects.get(pk=self.prod_class.pk)
        self.assertEqual(updated_instance.name, self.prod_class_edit_data["name"])
        self.assertEqual(updated_instance.short_name, self.prod_class_edit_data["short_name"])
        self.assertEqual(updated_instance.main_class.pk, self.prod_class_edit_data["main_class"])
        self.assertEqual(updated_instance.base_ei.pk, self.prod_class_edit_data["base_ei"])

    def test_class_update_view_can_save_a_POST_request_for_enum_class(self):
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=reverse("classes:edit_class", args=[self.enum_class.pk]),
            data=self.enum_class_edit_data
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)
        updated_instance = ClassStruct.objects.get(pk=self.enum_class.pk)
        self.assertEqual(updated_instance.name, self.enum_class_edit_data["name"])
        self.assertEqual(updated_instance.short_name, self.enum_class_edit_data["short_name"])
        self.assertEqual(updated_instance.main_class.pk, self.enum_class_edit_data["main_class"])

    def test_class_update_view_redirects_after_correct_POST_request_for_prod_class(self):
        response = self.client.post(
            path=reverse("classes:edit_class", args=[self.prod_class.pk]),
            data=self.prod_class_edit_data
        )
        redirect_url = reverse("classes:category_classes", args=[self.prod_class.main_class.pk])
        self.assertRedirects(response, redirect_url)

    def test_class_update_view_redirects_after_correct_POST_request_for_enum_class(self):
        response = self.client.post(
            path=reverse("classes:edit_class", args=[self.enum_class.pk]),
            data=self.enum_class_edit_data
        )
        redirect_url = reverse("classes:category_classes", args=[self.enum_class.main_class.pk])
        self.assertRedirects(response, redirect_url)

    def test_detected_classificator_cycle_validation_error_is_shown_on_page_for_prod_class(self):
        response = self.client.post(
            path=reverse("classes:edit_class", args=[self.prod_class.pk]),
            data=self.invalid_prod_class_edit_data
        )
        self.assertContains(response, escape(CLASSIFICATOR_CYCLE_ERROR))

    def test_detected_classificator_cycle_validation_error_is_shown_on_page_for_enum_class(self):
        response = self.client.post(
            path=reverse("classes:edit_class", args=[self.enum_class.pk]),
            data=self.invalid_enum_class_edit_data
        )
        self.assertContains(response, escape(CLASSIFICATOR_CYCLE_ERROR))
