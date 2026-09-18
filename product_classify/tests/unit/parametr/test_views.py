from django.urls import reverse
from django.utils.html import escape
from django.contrib.auth import get_user_model

from http import HTTPStatus
from urllib.parse import urlencode

from tests.unit.accounts.factories.user import UserFactory
from tests.unit.parametr.factories.parametr import ParametrFactory, ParametrFormData
from tests.unit.base import BaseUnitTestCase

from classes.models import ClassStruct
from classes.constants import ParamIds, EnumsIds

from accounts.constants import RoleCodes
from accounts.models import Role

from ei.models import Ei

from parametr.models import Parametr
from parametr.errors import ParametrErrors

User = get_user_model()


class ParametrListViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.ei = Ei.objects.first()

        cls.int_par = ParametrFactory(parametr_type=cls.int_type)
        cls.agregat_par = ParametrFactory(parametr_type=cls.agregat_type)

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.login_url = reverse("accounts:login")
        cls.url = reverse("parametr:list")

    def test_returns_302_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{self.login_url}?{urlencode({'next': self.url})}"
        self.assertRedirects(response, expected_url)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_list_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/list.html")

    def test_has_parameters_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("parameters", response.context)

    def test_renders_correct_number_of_parameters_without_argegat_params(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        expected_no_params = 1
        self.assertEqual(response.context["parameters"].count(), expected_no_params)


class ParametrDetailViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.ei = Ei.objects.first()

        cls.int_par = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.ei,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.login_url = reverse("accounts:login")
        cls.url = reverse("parametr:detail", args=[cls.int_par.pk])

    def test_returns_302_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{self.login_url}?{urlencode({'next': self.url})}"
        self.assertRedirects(response, expected_url)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_parametr_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/detail.html")

    def test_has_instance_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("parameter", response.context)

    def test_correctly_renders_product_information(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertContains(response, self.int_par.pk)
        self.assertContains(response, self.int_par.name)
        self.assertContains(response, self.int_par.short_name)
        self.assertContains(response, self.int_par.parametr_type.name)
        self.assertContains(response, self.int_par.par_ei.short_name)


class ParametrCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.str_enum_type = ClassStruct.objects.get(pk=EnumsIds.STRING)
        cls.img_enum_type = ClassStruct.objects.get(pk=EnumsIds.IMAGE)
        cls.par_ei = Ei.objects.first()

        cls.data = ParametrFormData(
            parametr_type=cls.int_type.pk,
            par_ei=cls.par_ei.pk,
        )
        cls.empty_name_data = ParametrFormData(
            name="",
            parametr_type=cls.int_type.pk,
            par_ei=cls.par_ei.pk,
        )
        cls.empty_short_name_data = ParametrFormData(
            short_name="",
            parametr_type=cls.int_type.pk,
            par_ei=cls.par_ei.pk,
        )
        cls.empty_parametr_type_data = ParametrFormData(
            parametr_type="",
            par_ei=cls.par_ei.pk,
        )
        cls.invalid_str_data = ParametrFormData(
            parametr_type=cls.str_enum_type.pk,
            par_ei=cls.par_ei.pk,
        )
        cls.invalid_img_data = ParametrFormData(
            parametr_type=cls.img_enum_type.pk,
            par_ei=cls.par_ei.pk,
        )
        cls.invalid_agr_data = ParametrFormData(
            parametr_type=cls.agr_type.pk,
            par_ei=cls.par_ei.pk,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("parametr:add")
        cls.redirect_url = reverse("parametr:list")

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_parametr_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/parametr.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        count_before = Parametr.objects.count()
        self.client.post(self.url, data=self.data)
        self.assertEqual(Parametr.objects.count(), count_before + 1)

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_name_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.empty_name_data)
        self.assertContains(response, ParametrErrors.EMPTY_NAME)

    def test_empty_short_name_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.empty_short_name_data)
        self.assertContains(response, ParametrErrors.EMPTY_SHORT_NAME)

    def test_empty_parametr_type_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.empty_parametr_type_data)
        self.assertContains(response, ParametrErrors.EMPTY_PAR_TYPE)

    def test_string_enum_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.invalid_str_data)
        self.assertContains(response, escape(ParametrErrors.STRING_ENUM))

    def test_image_enum_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.invalid_img_data)
        self.assertContains(response, escape(ParametrErrors.IMAGE_ENUM))

    def test_agregat_enum_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.invalid_agr_data)
        self.assertContains(response, escape(ParametrErrors.AGREGAT))


class ParametrUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.par_ei = Ei.objects.first()

        cls.instance = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )

        cls.update_data = ParametrFormData(
            parametr_type=cls.int_type.pk,
            par_ei=cls.par_ei.pk,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("parametr:edit", args=[cls.instance.pk])
        cls.redirect_url = reverse("parametr:detail", args=[cls.instance.pk])

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_parametr_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/parametr.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.update_data)
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.name, self.update_data["name"])
        self.assertEqual(self.instance.short_name, self.update_data["short_name"])
        self.assertEqual(self.instance.par_ei.pk, self.update_data["par_ei"])
        self.assertEqual(self.instance.parametr_type.pk, self.update_data["parametr_type"])

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.update_data)
        self.assertRedirects(response, self.redirect_url)


class ParametrDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.par_ei = Ei.objects.first()

        cls.instance = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("parametr:delete", args=[cls.instance.pk])
        cls.redirect_url = reverse("parametr:list")

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_parametr_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "parametr/parametr.html")

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url)
        self.assertEqual(Parametr.objects.count(), 0)

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)
