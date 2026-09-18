from django.urls import reverse
from django.contrib.auth import get_user_model

from urllib.parse import urlencode
from http import HTTPStatus

from tests.unit.agregat.factories.agregat import AgregatFactory
from tests.unit.parametr.factories.parametr import ParametrFactory
from tests.unit.base import BaseUnitTestCase
from tests.unit.accounts.factories.user import UserFactory

from classes.constants import ParamIds
from classes.models import ClassStruct

from ei.models import Ei

from accounts.constants import RoleCodes
from accounts.models import Role

from agregat.errors import AgregatErrors
from agregat.models import Agregat

User = get_user_model()


class AgregatListViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.par_ei = Ei.objects.first()

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.par2 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.agr = ParametrFactory(
            parametr_type=cls.agr_type,
            par_ei=cls.par_ei,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.login_url = reverse("accounts:login")
        cls.url = reverse("agregat:list")

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
        self.assertTemplateUsed(response, "agregat/list.html")

    def test_has_agregats_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("agregats", response.context)

    def test_renders_correct_number_of_agregats(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["agregats"].count(), 1)


class AgregatParametrCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.par_ei = Ei.objects.first()

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.par2 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.agr = ParametrFactory(
            parametr_type=cls.agr_type,
            par_ei=cls.par_ei,
        )

        cls.valid_data = {
            "agr": cls.agr.pk,
            "par": cls.par1.pk,
        }

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("agregat:add", args=[cls.agr.pk])
        cls.redirect_url = reverse("agregat:detail", args=[cls.agr.pk])

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

    def test_uses_agregat_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "agregat/agregat.html")

    def test_has_agregat_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        count_before = Agregat.objects.filter(agr=self.agr).count()
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(
            Agregat.objects.filter(agr=self.agr).count(),
            count_before + 1,
        )
        instance = Agregat.objects.last()
        self.assertEqual(instance.agr.pk, self.valid_data["agr"])
        self.assertEqual(instance.par.pk, self.valid_data["par"])
        self.assertEqual(instance.num, 1)

    def test_redirects_after_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.redirect_url)


class AgregatParametrDetailViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.par_ei = Ei.objects.first()

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.par2 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.agr = ParametrFactory(
            parametr_type=cls.agr_type,
            par_ei=cls.par_ei,
        )

        cls.agregat1 = AgregatFactory(agr=cls.agr, par=cls.par1, num=1)
        cls.agregat2 = AgregatFactory(agr=cls.agr, par=cls.par2, num=2)

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("agregat:detail", kwargs={"agregat_id": cls.agr.pk})

    def test_returns_302_for_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_detail_html(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "agregat/detail.html")

    def test_renders_agregat_instance(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("agregat", response.context)

    def test_renders_agregat_parameters(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("agr_parametrs", response.context)

    def test_correctly_renders_information_about_agregat(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertContains(response, self.agr.name)
        self.assertContains(response, self.par1.name)
        self.assertContains(response, self.par2.name)


class ChangeNumViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.par_ei = Ei.objects.first()

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.par2 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.agr = ParametrFactory(
            parametr_type=cls.agr_type,
            par_ei=cls.par_ei,
        )

        cls.pair1 = AgregatFactory(agr=cls.agr, par=cls.par1, num=1)
        cls.pair2 = AgregatFactory(agr=cls.agr, par=cls.par2, num=2)

        cls.valid_data = {
            "par_1": cls.pair1.pk,
            "par_2": cls.pair2.pk,
        }
        cls.empty_p1_data = {
            "par_1": "",
            "par_2": cls.pair2.pk,
        }
        cls.empty_p2_data = {
            "par_1": cls.pair1.pk,
            "par_2": "",
        }
        cls.same_params_data = {
            "par_1": cls.pair1.pk,
            "par_2": cls.pair1.pk,
        }

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("agregat:change_num", kwargs={"agregat_id": cls.agr.pk})
        cls.redirect_url = reverse("agregat:detail", kwargs={"agregat_id": cls.agr.pk})

    def test_returns_302_for_anonymous_user(self):
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

    def test_uses_change_agr_num_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "agregat/change_agr_num.html")

    def test_has_fastener_classes_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_has_instance_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_can_save_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.valid_data)
        self.pair1.refresh_from_db()
        self.pair2.refresh_from_db()
        self.assertEqual(self.pair1.num, 2)
        self.assertEqual(self.pair2.num, 1)

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_first_param_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.empty_p1_data)
        self.assertContains(response, AgregatErrors.EMPTY_FIRST_PARAM)

    def test_empty_second_param_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.empty_p2_data)
        self.assertContains(response, AgregatErrors.EMPTY_SECOND_PARAM)

    def test_same_params_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.same_params_data)
        self.assertContains(response, AgregatErrors.SAME_PARAMS)


class AgregatParametrDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.agr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.par_ei = Ei.objects.first()

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.par2 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.par3 = ParametrFactory(
            parametr_type=cls.int_type,
            par_ei=cls.par_ei,
        )
        cls.agr = ParametrFactory(
            parametr_type=cls.agr_type,
            par_ei=cls.par_ei,
        )

        cls.pair1 = AgregatFactory(agr=cls.agr, par=cls.par1, num=1)
        cls.pair2 = AgregatFactory(agr=cls.agr, par=cls.par2, num=2)
        cls.pair3 = AgregatFactory(agr=cls.agr, par=cls.par3, num=3)

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.redirect_url = reverse("agregat:detail", kwargs={
            "agregat_id": cls.agr.pk,
        })

    def _get_url(self, agr_pk: int, par_pk: int):
        return reverse("agregat:delete", kwargs={
            "agregat_id": agr_pk,
            "param_id": par_pk,
        })

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(self._get_url(self.agr.pk, self.par1.pk))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(self._get_url(self.agr.pk, self.par1.pk))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self._get_url(self.agr.pk, self.par1.pk))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self._get_url(self.agr.pk, self.par1.pk))
        self.assertTemplateUsed(response, "agregat/agregat.html")

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.assertEqual(Agregat.objects.filter(agr=self.agr).count(), 3)
        self.client.post(self._get_url(self.agr.pk, self.par1.pk))
        self.assertEqual(Agregat.objects.filter(agr=self.agr).count(), 2)

    def test_correctly_recalculates_num_fields_if_we_delete_first_par(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self._get_url(self.agr.pk, self.par1.pk))
        pair1 = Agregat.objects.first()
        self.assertEqual(pair1.num, 1)
        pair2 = Agregat.objects.last()
        self.assertEqual(pair2.num, 2)

    def test_correctly_recalculates_num_fields_if_we_delete_par_in_the_middle(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self._get_url(self.agr.pk, self.par2.pk))
        pair1 = Agregat.objects.first()
        self.assertEqual(pair1.num, 1)
        pair2 = Agregat.objects.last()
        self.assertEqual(pair2.num, 2)

    def test_correctly_recalculates_num_fields_if_we_delete_last_par(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self._get_url(self.agr.pk, self.par3.pk))
        pair1 = Agregat.objects.first()
        self.assertEqual(pair1.num, 1)
        pair2 = Agregat.objects.last()
        self.assertEqual(pair2.num, 2)

    def test_redirect_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self._get_url(self.agr.pk, self.par1.pk))
        self.assertRedirects(response, self.redirect_url)
