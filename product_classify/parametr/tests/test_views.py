from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

from faker import Faker

from classes.models import ClassStruct
from classes.constants import ParamIds, EnumsIds

from ei.models import Ei

from parametr.models import Parametr
from parametr.constants import ParametrConsts
from parametr.errors import ParametrErrors


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


class ParametrCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.str_enum_type = ClassStruct.objects.get(pk=EnumsIds.STRING)
        cls.img_enum_type = ClassStruct.objects.get(pk=EnumsIds.IMAGE)
        cls.par_ei = Ei.objects.first()

        name = cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH]
        short_name = cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH]

        cls.data = {
            "name": name,
            "short_name": short_name,
            "parametr_type": cls.int_type.pk,
            "par_ei": cls.par_ei.pk,
        }
        cls.empty_name_data = {
            "name": "",
            "short_name": short_name,
            "parametr_type": cls.int_type.pk,
            "par_ei": cls.par_ei.pk,
        }
        cls.empty_short_name_data = {
            "name": name,
            "short_name": "",
            "parametr_type": cls.int_type.pk,
            "par_ei": cls.par_ei.pk,
        }
        cls.empty_parametr_type_data = {
            "name": name,
            "short_name": short_name,
            "parametr_type": "",
            "par_ei": cls.par_ei.pk,
        }
        cls.invalid_str_data = {
            "name": name,
            "short_name": short_name,
            "parametr_type": cls.str_enum_type.pk,
            "par_ei": cls.par_ei.pk,
        }
        cls.invalid_img_data = {
            "name": name,
            "short_name": short_name,
            "parametr_type": cls.img_enum_type.pk,
            "par_ei": cls.par_ei.pk,
        }
        cls.invalid_agr_data = {
            "name": name,
            "short_name": short_name,
            "parametr_type": cls.agr_type.pk,
            "par_ei": cls.par_ei.pk,
        }

        cls.url = reverse("parametr:add")
        cls.redirect_url = reverse("parametr:list")

    def test_parametr_create_view_uses_parametr_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/parametr.html")

    def test_parametr_create_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_parametr_create_view_can_save_a_POST_request(self):
        count_before = Parametr.objects.count()
        self.client.post(self.url, data=self.data)
        self.assertEqual(Parametr.objects.count(), count_before + 1)

    def test_parametr_create_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_name_data)
        self.assertContains(response, ParametrErrors.EMPTY_NAME)

    def test_empty_short_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_short_name_data)
        self.assertContains(response, ParametrErrors.EMPTY_SHORT_NAME)

    def test_empty_parametr_type_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_parametr_type_data)
        self.assertContains(response, ParametrErrors.EMPTY_PAR_TYPE)

    def test_string_enum_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.invalid_str_data)
        self.assertContains(response, escape(ParametrErrors.STRING_ENUM))

    def test_image_enum_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.invalid_img_data)
        self.assertContains(response, escape(ParametrErrors.IMAGE_ENUM))

    def test_agregat_enum_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.invalid_agr_data)
        self.assertContains(response, escape(ParametrErrors.AGREGAT))


class ParametrUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.par_ei = Ei.objects.first()

        old_name = cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH]
        old_short_name = cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH]

        cls.instance = Parametr.objects.create(
            name=old_name,
            short_name=old_short_name,
            parametr_type=cls.int_type,
            par_ei=cls.par_ei
        )

        new_name = cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH]
        short_new_name = cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH]

        cls.update_data = {
            "name": new_name,
            "short_name": short_new_name,
            "parametr_type": cls.int_type.pk,
            "par_ei": cls.par_ei.pk
        }

        cls.url = reverse("parametr:edit", args=[cls.instance.pk])
        cls.redirect_url = reverse("parametr:detail", args=[cls.instance.pk])

    def test_parametr_update_view_uses_parametr_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/parametr.html")

    def test_parametr_update_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_parametr_update_view_can_save_a_POST_request(self):
        self.client.post(self.url, data=self.update_data)
        parametr = Parametr.objects.last()
        self.assertEqual(parametr.name, self.update_data["name"])
        self.assertEqual(parametr.short_name, self.update_data["short_name"])
        self.assertEqual(parametr.par_ei.pk, self.update_data["par_ei"])
        self.assertEqual(parametr.parametr_type.pk, self.update_data["parametr_type"])

    def test_parametr_update_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.update_data)
        self.assertRedirects(response, self.redirect_url)
