from django.test import TestCase
from django.urls import reverse

from faker import Faker

from classes.constants import ParamIds
from classes.models import ClassStruct
from parametr.models import Parametr
from parametr.constants import ParametrConsts
from ei.models import Ei


class AgregatListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.par_ei = Ei.objects.first()

        cls.par1 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_type,
            par_ei=cls.par_ei
        )
        cls.par2 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_type,
            par_ei=cls.par_ei
        )
        cls.agr = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.agr_type,
            par_ei=cls.par_ei,
        )

        cls.url = reverse("agregat:list")

    def test_agregat_list_view_uses_list_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "agregat/list.html")

    def test_agregat_list_view_has_agregats_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("agregats", response.context)

    def test_agregat_list_view_renders_correct_number_of_agregats(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["agregats"].count(), 1)
