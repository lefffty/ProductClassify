from django.test import TestCase
from django.urls import reverse

from faker import Faker
from random import randint

from ei.models import Ei
from ei.constants import EiConsts


class EiListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("ei:list")

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
        cls.url = reverse("ei:detail", args=[cls.instance.pk])

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


class EiCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.main_class = Ei.objects.first()
        cls.url = reverse("ei:add")
        cls.redirect_url = reverse("ei:list")

        cls.data = {
            "name": cls.fake.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:EiConsts.SHORT_NAME_MAX_LENGTH],
            "code": cls.fake.postcode()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": randint(1, 100),
            "main_class": cls.main_class.pk,
        }

    def test_ei_create_view_uses_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/ei.html")

    def test_ei_create_view_renders_ei_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_has_fastener_classes_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_ei_create_view_can_save_a_POST_request(self):
        count_before = Ei.objects.count()
        self.client.post(self.url, data=self.data)
        self.assertEqual(Ei.objects.count(), count_before + 1)

    def test_ei_create_view_redirects_after_a_POST_request(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.redirect_url)


class EiDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ei_id = Ei.objects.last().pk
        cls.url = reverse("ei:delete", args=[cls.ei_id])
        cls.redirect_url = reverse("ei:list")

    def test_ei_delete_view_uses_ei_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/ei.html")

    def test_ei_delete_view_can_save_a_POST_request(self):
        count_before = Ei.objects.count()
        self.client.post(self.url)
        self.assertEqual(Ei.objects.count(), count_before - 1)

    def test_ei_delete_view_redirects_after_successful_POST_request(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class EiUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ei = Ei.objects.last()
        cls.ei_id = cls.ei.pk
        cls.url = reverse("ei:edit", args=[cls.ei_id])
        cls.redirect_url = reverse("ei:detail", args=[cls.ei_id])
        cls.fake = Faker()

        cls.data = {
            "name": cls.fake.name()[:EiConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:EiConsts.SHORT_NAME_MAX_LENGTH].strip(),
            "code": cls.fake.postcode()[:EiConsts.CODE_MAX_LENGTH],
            "convert_factor": randint(1, 100),
            "main_class": cls.ei.main_class.pk,
        }

    def test_ei_update_view_uses_ei_update_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "ei/ei.html")

    def test_ei_update_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_ei_update_view_can_save_a_POST_request(self):
        self.client.post(self.url, data=self.data)
        ei = Ei.objects.last()
        self.assertEqual(ei.name, self.data["name"])
        self.assertEqual(ei.short_name, self.data["short_name"])
        self.assertEqual(ei.code, self.data["code"])
        self.assertEqual(ei.convert_factor, self.data["convert_factor"])
        self.assertEqual(ei.main_class.pk, self.data["main_class"])

    def test_ei_update_view_redirect_after_successful_POST_request(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.redirect_url)
