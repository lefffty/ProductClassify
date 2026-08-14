from django.test import TestCase
from django.urls import reverse

from faker import Faker
from http import HTTPStatus

from classes.constants import ParamIds
from classes.models import ClassStruct
from parametr.models import Parametr
from parametr.constants import ParametrConsts
from ei.models import Ei

from agregat.errors import AgregatErrors
from agregat.models import Agregat


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


class ChangeNumViewTest(TestCase):
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

        cls.pairs = Agregat.objects.bulk_create((
            Agregat(agr=cls.agr, par=cls.par1, num=1),
            Agregat(agr=cls.agr, par=cls.par2, num=2)
        ))

        cls.valid_data = {
            "par_1": cls.pairs[0].pk,
            "par_2": cls.pairs[1].pk
        }
        cls.empty_p1_data = {
            "par_1": "",
            "par_2": cls.pairs[1].pk
        }
        cls.empty_p2_data = {
            "par_1": cls.pairs[0].pk,
            "par_2": ""
        }
        cls.same_params_data = {
            "par_1": cls.pairs[0].pk,
            "par_2": cls.pairs[0].pk
        }

        cls.url = reverse("agregat:change_num", kwargs={"agregat_id": cls.agr.pk})
        cls.redirect_url = reverse("agregat:detail", kwargs={"agregat_id": cls.agr.pk})

    def test_change_num_view_uses_change_agr_num_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "agregat/change_agr_num.html")

    def test_change_num_view_has_fastener_classes_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_change_num_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_change_num_view_has_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_change_num_view_can_save_POST_request(self):
        self.client.post(self.url, data=self.valid_data)
        self.pairs[0].refresh_from_db()
        self.pairs[1].refresh_from_db()
        self.assertEqual(self.pairs[0].num, 2)
        self.assertEqual(self.pairs[1].num, 1)

    def test_change_num_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_first_param_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_p1_data)
        self.assertContains(response, AgregatErrors.EMPTY_FIRST_PARAM)

    def test_empty_second_param_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_p2_data)
        self.assertContains(response, AgregatErrors.EMPTY_SECOND_PARAM)

    def test_same_params_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.same_params_data)
        self.assertContains(response, AgregatErrors.SAME_PARAMS)


class AgregatParametrDeleteViewTest(TestCase):
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
        cls.par3 = Parametr.objects.create(
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

        cls.pairs = Agregat.objects.bulk_create((
            Agregat(agr=cls.agr, par=cls.par1, num=1),
            Agregat(agr=cls.agr, par=cls.par2, num=2),
            Agregat(agr=cls.agr, par=cls.par3, num=3),
        ))
        cls.redirect_url = reverse("agregat:detail", kwargs={
            "agregat_id": cls.agr.pk
        })

    def _get_url(self, agr_pk: int, par_pk: int):
        return reverse("agregat:delete", kwargs={
            "agregat_id": agr_pk,
            "param_id": par_pk
        })

    def test_agregat_parametr_sdelete_view_uses_template(self):
        response = self.client.get(self._get_url(self.agr.pk, self.par1.pk))
        self.assertTemplateUsed(response, "agregat/agregat.html")

    def test_agregat_parametr_delete_view_can_save_a_POST_request(self):
        self.assertEqual(Agregat.objects.filter(agr=self.agr).count(), 3)
        self.client.post(self._get_url(self.agr.pk, self.par1.pk))
        self.assertEqual(Agregat.objects.filter(agr=self.agr).count(), 2)

    def test_agregat_parametr_delete_view_correctly_recalculates_num_fields_if_we_delete_first_par(self):
        self.client.post(self._get_url(self.agr.pk, self.par1.pk))
        pair1 = Agregat.objects.first()
        self.assertEqual(pair1.num, 1)
        pair2 = Agregat.objects.last()
        self.assertEqual(pair2.num, 2)

    def test_agregat_parametr_delete_view_correctly_recalculates_num_fields_if_we_delete_par_in_the_middle(self):
        self.client.post(self._get_url(self.agr.pk, self.par2.pk))
        pair1 = Agregat.objects.first()
        self.assertEqual(pair1.num, 1)
        pair2 = Agregat.objects.last()
        self.assertEqual(pair2.num, 2)

    def test_agregat_parametr_delete_view_correctly_recalculates_num_fields_if_we_delete_last_par(self):
        self.client.post(self._get_url(self.agr.pk, self.par3.pk))
        pair1 = Agregat.objects.first()
        self.assertEqual(pair1.num, 1)
        pair2 = Agregat.objects.last()
        self.assertEqual(pair2.num, 2)

    def test_agregat_parametr_delete_view_redirect_after_POST_request(self):
        response = self.client.post(self._get_url(self.agr.pk, self.par1.pk))
        self.assertRedirects(response, self.redirect_url)
