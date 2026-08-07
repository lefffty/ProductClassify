from django.test import TestCase
from django.urls import reverse


class MainPageTemplateViewTest(TestCase):
    def test_main_page_template_view_uses_index_template(self):
        response = self.client.get(reverse("classes:index"))
        self.assertTemplateUsed(response, "classes/index.html")

    def test_fastener_classes_are_in_context(self):
        response = self.client.get(reverse("classes:index"))
        self.assertIn("fastener_classes", response.context)

    def test_fastener_classes_count_is_correct(self):
        response = self.client.get(reverse("classes:index"))
        self.assertEqual(len(response.context["fastener_classes"]), 3)

    def test_renders_nav_bar(self):
        response = self.client.get(reverse("classes:index"))
        self.assertContains(response, '<nav id="menu">')
