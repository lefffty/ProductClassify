from django.test import TestCase
from django.urls import reverse


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
