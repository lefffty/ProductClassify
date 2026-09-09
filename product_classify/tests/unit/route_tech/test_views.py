from django.urls import reverse
from django.utils.html import escape

from faker import Faker

from classes.models import ClassStruct
from classes.constants import MetaConsts

from route_tech.models import EconomicActivitySubject
from route_tech.constants import EASConsts
from route_tech.errors import EASErrors

from tests.unit.base import BaseUnitTestCase


class EASCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)

        cls.parent_subject = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None
        )

        cls.name = cls.faker.name()[:EASConsts.NAME_MAX_LENGTH]
        cls.short_name = cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH]
        cls.new_name = cls.faker.name()[:EASConsts.NAME_MAX_LENGTH]
        cls.new_short_name = cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH]

        cls.valid_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": ""
        }

        cls.valid_data_with_parent = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": cls.parent_subject.pk
        }

        cls.empty_name_data = {
            "name": "",
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": ""
        }

        cls.empty_short_name_data = {
            "name": cls.name,
            "short_name": "",
            "main_class": cls.enterprise.pk,
            "main_subject": ""
        }

        cls.empty_main_class_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": "",
            "main_subject": ""
        }

        cls.url = reverse("route_tech:add_eas")
        cls.redirect_url = reverse("classes:index")

    def test_eas_create_view_uses_eas_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/eas.html")

    def test_eas_create_view_uses_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_eas_create_view_can_save_a_POST_request_with_non_parent(self):
        self.client.post(self.url, self.valid_data)
        eas = EconomicActivitySubject.objects.last()
        self.assertIsNotNone(eas.pk)
        self.assertEqual(eas.name, self.valid_data["name"])
        self.assertEqual(eas.short_name, self.valid_data["short_name"])
        self.assertEqual(eas.main_class.pk, self.valid_data["main_class"])
        self.assertIsNone(eas.main_subject)

    def test_eas_create_view_can_save_a_POST_request_with_parent(self):
        self.client.post(self.url, self.valid_data_with_parent)
        eas = EconomicActivitySubject.objects.last()
        self.assertIsNotNone(eas.pk)
        self.assertEqual(eas.name, self.valid_data["name"])
        self.assertEqual(eas.short_name, self.valid_data["short_name"])
        self.assertEqual(eas.main_class.pk, self.valid_data["main_class"])
        self.assertIsNotNone(eas.main_subject.pk)

    def test_eas_create_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_data)
        EconomicActivitySubject.objects.last()
        self.assertRedirects(response, self.redirect_url)

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_name_data)
        self.assertContains(response, escape(EASErrors.EMPTY_NAME))

    def test_empty_short_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_short_name_data)
        self.assertContains(response, escape(EASErrors.EMPTY_SHORT_NAME))

    def test_empty_main_class_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_main_class_data)
        self.assertContains(response, escape(EASErrors.EMPTY_MAIN_CLASS))


class EASUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)

        cls.parent_subject = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None
        )

        cls.subject = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=cls.parent_subject
        )

        cls.new_name = cls.faker.name()[:EASConsts.NAME_MAX_LENGTH]
        cls.new_short_name = cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH]

        cls.valid_update_data = {
            "name": cls.new_name,
            "short_name": cls.new_short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": cls.parent_subject.pk
        }

        cls.url = reverse("route_tech:edit_eas", args=[cls.subject.pk])
        cls.redirect_url = reverse("route_tech:detail_eas", args=[cls.subject.pk])

    def test_eas_update_view_uses_eas_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/eas.html")

    def test_eas_update_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_eas_update_view_can_save_a_POST_request(self):
        self.client.post(self.url, self.valid_update_data)
        eas = EconomicActivitySubject.objects.last()
        self.assertEqual(eas.name, self.valid_update_data["name"])
        self.assertEqual(eas.short_name, self.valid_update_data["short_name"])
        self.assertEqual(eas.main_class.pk, MetaConsts.ENTERPRISE)
        self.assertEqual(eas.main_subject.pk, self.parent_subject.pk)

    def test_eas_update_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_update_data)
        self.assertRedirects(response, self.redirect_url)
