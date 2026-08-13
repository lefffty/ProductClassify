from django.test import TestCase
from django.urls import reverse

from faker import Faker

from classes.models import ClassStruct
from classes.constants import ParamIds

from ei.models import Ei

from parametr.models import Parametr
from parametr.constants import ParametrConsts


class ParametrListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.ei = Ei.objects.first()

        cls.int_par = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_type,
            par_ei=cls.ei,
        )
        cls.agregat_par = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.agregat_type,
            par_ei=None,
        )

        cls.url = reverse("parametr:list")

    def test_parametr_list_view_uses_list_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/list.html")

    def test_parametr_list_view_has_parameters_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("parameters", response.context)

    def test_parametr_list_renders_correct_number_of_parameters_without_argegat_params(self):
        response = self.client.get(self.url)
        expected_no_params = 1
        self.assertEqual(response.context["parameters"].count(), expected_no_params)


class ParametrDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.ei = Ei.objects.first()

        cls.int_par = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_type,
            par_ei=cls.ei
        )

        cls.url = reverse("parametr:detail", args=[cls.int_par.pk])

    def test_parametr_detail_view_uses_parametr_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/detail.html")

    def test_parametr_detail_view_has_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("parameter", response.context)

    def test_parametr_detail_view_correctly_renders_product_information(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.int_par.pk)
        self.assertContains(response, self.int_par.name)
        self.assertContains(response, self.int_par.short_name)
        self.assertContains(response, self.int_par.parametr_type.name)
        self.assertContains(response, self.int_par.par_ei)
