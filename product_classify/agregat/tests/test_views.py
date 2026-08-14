from django.test import TestCase
from django.urls import reverse

from faker import Faker

from classes.constants import ParamIds
from classes.models import ClassStruct
from parametr.models import Parametr
from parametr.constants import ParametrConsts
from agregat.models import Agregat
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


class AgregatParametrCreateViewTest(TestCase):
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
            par_ei=cls.par_ei
        )

        cls.valid_data = {
            "agr": cls.agr.pk,
            "par": cls.par1.pk,
        }

        cls.url = reverse("agregat:add", args=[cls.agr.pk])
        cls.redirect_url = reverse("agregat:detail", args=[cls.agr.pk])

    def test_agregat_parametr_create_view_uses_agregat_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "agregat/agregat.html")

    def test_agregat_parametr_create_view_has_agregat_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_agregat_parametr_create_view_can_save_a_POST_request(self):
        count_before = Agregat.objects.filter(pk=self.agr.pk).count()
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(
            Agregat.objects.filter(agr=self.agr).count(),
            count_before + 1
        )
        instance = Agregat.objects.last()
        self.assertEqual(instance.agr.pk, self.valid_data["agr"])
        self.assertEqual(instance.par.pk, self.valid_data["par"])
        self.assertEqual(instance.num, 1)

    def test_agregat_parametr_create_view_redirects_after_a_POST_request(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.redirect_url)


class AgregatParametrDetailViewTest(TestCase):
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
            par_ei=cls.par_ei
        )

        Agregat.objects.bulk_create((
            Agregat(agr=cls.agr, par=cls.par1, num=1),
            Agregat(agr=cls.agr, par=cls.par2, num=2)
        ))

        cls.url = reverse("agregat:detail", kwargs={"agregat_id": cls.agr.pk})

    def test_agregat_parametr_detail_view_uses_detail_html(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "agregat/detail.html")

    def test_agregat_parametr_detail_view_renders_agregat_instance(self):
        response = self.client.get(self.url)
        self.assertIn("agregat", response.context)

    def test_agregat_parametr_detail_view_renders_agregat_parameters(self):
        response = self.client.get(self.url)
        self.assertIn("agr_parametrs", response.context)

    def test_agregat_parametr_detail_view_correctly_renders_information_about_agregat(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.agr.name)
        self.assertContains(response, self.par1.name)
        self.assertContains(response, self.par2.name)
