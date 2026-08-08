from django.test import TestCase
from django.urls import reverse

from http import HTTPStatus

from classes.models import ClassStruct

from parameterized import parameterized


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
