from django.test import TestCase
from django.urls import reverse

from ei.models import Ei


class EiListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("ei:ei_list")

    def test_ei_list_view_uses_ei_list_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/list.html")

    def test_has_eis_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("eis", response.context)

    def test_has_fastener_classes_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)


class EiDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.instance = Ei.objects.first()
        cls.url = reverse("ei:ei_detail", args=[cls.instance.pk])

    def test_ei_detail_view_uses_ei_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/detail.html")

    def test_has_ei_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("ei", response.context)

    def test_has_fastener_classes_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_ei_data_is_successfully_displayed_on_page(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.instance.pk)
        self.assertContains(response, self.instance.name)
        self.assertContains(response, self.instance.short_name)
        self.assertContains(response, self.instance.convert_factor)
