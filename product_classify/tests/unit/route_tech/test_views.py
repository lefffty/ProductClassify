from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.html import escape
from django.contrib.auth import get_user_model

from decimal import Decimal
from faker import Faker
from http import HTTPStatus

from classes.models import ClassStruct
from classes.constants import (
    MetaConsts,
    ProductsConsts,
    OperationConsts,
    ProfessionConsts,
    ClassStructConsts,
    QualificationConsts,
)

from accounts.constants import RoleCodes, UserConsts
from accounts.models import Role

from ei.models import Ei

from products.constants import ProdConsts
from products.models import Prod

from route_tech.models import EconomicActivitySubject, GroupWorkingCenter, ProdOperation, ProdOperationPos
from route_tech.constants import EASConsts, GWCConsts
from route_tech.forms import ProdOperationPosFormSet
from route_tech.errors import EASErrors, GWCErrors, ProdOperErrors

from tests.unit.base import BaseUnitTestCase

User = get_user_model()


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

    def test_uses_eas_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/eas/eas.html")

    def test_uses_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request_with_non_parent(self):
        self.client.post(self.url, self.valid_data)
        eas = EconomicActivitySubject.objects.last()
        self.assertIsNotNone(eas.pk)
        self.assertEqual(eas.name, self.valid_data["name"])
        self.assertEqual(eas.short_name, self.valid_data["short_name"])
        self.assertEqual(eas.main_class.pk, self.valid_data["main_class"])
        self.assertIsNone(eas.main_subject)

    def test_can_save_a_POST_request_with_parent(self):
        self.client.post(self.url, self.valid_data_with_parent)
        eas = EconomicActivitySubject.objects.last()
        self.assertIsNotNone(eas.pk)
        self.assertEqual(eas.name, self.valid_data["name"])
        self.assertEqual(eas.short_name, self.valid_data["short_name"])
        self.assertEqual(eas.main_class.pk, self.valid_data["main_class"])
        self.assertIsNotNone(eas.main_subject.pk)

    def test_redirects_after_POST_request(self):
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

    def test_uses_eas_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/eas/eas.html")

    def test_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url, self.valid_update_data)
        eas = EconomicActivitySubject.objects.last()
        self.assertEqual(eas.name, self.valid_update_data["name"])
        self.assertEqual(eas.short_name, self.valid_update_data["short_name"])
        self.assertEqual(eas.main_class.pk, MetaConsts.ENTERPRISE)
        self.assertEqual(eas.main_subject.pk, self.parent_subject.pk)

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_update_data)
        self.assertRedirects(response, self.redirect_url)


class EASDetailViewTest(BaseUnitTestCase):
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

        cls.url = reverse("route_tech:detail_eas", args=[cls.subject.pk])

    def test_uses_eas_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/eas/detail.html")

    def test_renders_correct_information(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.subject.name)
        self.assertContains(response, self.subject.short_name)
        self.assertContains(response, self.subject.main_subject)
        children: list[EconomicActivitySubject] = self.subject.children.all()
        for child in children:
            self.assertContains(response, child.name)
            self.assertContains(response, child.short_name)


class EASDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)

        cls.subject = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None
        )

        cls.url = reverse("route_tech:delete_eas", args=[cls.subject.pk])
        cls.redirect_url = reverse("classes:index")

    def test_uses_eas_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/eas/eas.html")

    def test_can_save_a_POST_request(self):
        self.client.post(self.url)
        self.assertEqual(EconomicActivitySubject.objects.count(), 0)

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class GWCCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.enterpise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.stand = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.means_of_labor,
        )

        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterpise,
            main_subject=None
        )

        cls.name = cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH]
        cls.short_name = cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH]
        cls.place = cls.faker.random_int(min=1, max=100)

        cls.valid_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.stand.pk,
            "eas": cls.eas.pk,
            "place": cls.place
        }

        cls.empty_name_data = {
            "name": "",
            "short_name": cls.short_name,
            "main_class": cls.stand.pk,
            "eas": cls.eas.pk,
            "place": cls.place
        }

        cls.empty_short_name_data = {
            "name": cls.name,
            "short_name": "",
            "main_class": cls.stand.pk,
            "eas": cls.eas.pk,
            "place": cls.place
        }

        cls.empty_main_class_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": "",
            "eas": cls.eas.pk,
            "place": cls.place
        }

        cls.empty_eas_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.stand.pk,
            "eas": "",
            "place": cls.place
        }
        cls.empty_place_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.stand.pk,
            "eas": cls.eas.pk,
            "place": ""
        }

        cls.invalid_place_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.stand.pk,
            "eas": cls.eas.pk,
            "place": -1
        }

        cls.url = reverse("route_tech:add_gwc")
        cls.redirect_url = reverse("classes:index")

    def test_uses_gwc_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/gwc/gwc.html")

    def test_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url, self.valid_data)
        gwc = GroupWorkingCenter.objects.last()
        self.assertEqual(gwc.name, self.valid_data["name"])
        self.assertEqual(gwc.short_name, self.valid_data["short_name"])
        self.assertEqual(gwc.place, self.valid_data["place"])
        self.assertEqual(gwc.main_class.pk, self.valid_data["main_class"])
        self.assertEqual(gwc.eas.pk, self.valid_data["eas"])

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_name_data)
        self.assertContains(response, escape(GWCErrors.EMPTY_NAME))

    def test_empty_short_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_short_name_data)
        self.assertContains(response, escape(GWCErrors.EMPTY_SHORT_NAME))

    def test_empty_main_class_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_main_class_data)
        self.assertContains(response, escape(GWCErrors.EMPTY_MAIN_CLASS))

    def test_empty_eas_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_eas_data)
        self.assertContains(response, escape(GWCErrors.EMPTY_EAS))

    def test_empty_place_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_place_data)
        self.assertContains(response, escape(GWCErrors.EMPTY_PLACE))

    def test_invalid_place_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.invalid_place_data)
        self.assertContains(response, escape(GWCErrors.INVALID_PLACE))


class GWCUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.stand = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.means_of_labor,
        )

        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None
        )

        cls.gwc = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=100)
        )

        cls.new_name = cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH]
        cls.new_short_name = cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH]
        cls.new_place = cls.faker.random_int(min=1, max=100)

        cls.valid_update_data = {
            "name": cls.new_name,
            "short_name": cls.new_short_name,
            "main_class": cls.stand.pk,
            "eas": cls.eas.pk,
            "place": cls.new_place
        }

        cls.update_data_with_another_eas = {
            "name": cls.new_name,
            "short_name": cls.new_short_name,
            "main_class": cls.stand.pk,
            "eas": cls.eas.pk,
            "place": cls.new_place
        }

        cls.url = reverse("route_tech:edit_gwc", args=[cls.gwc.pk])
        cls.redirect_url = reverse("route_tech:detail_gwc", args=[cls.gwc.pk])

    def test_uses_gwc_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/gwc/gwc.html")

    def test_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url, self.valid_update_data)
        gwc = GroupWorkingCenter.objects.last()
        self.assertEqual(gwc.name, self.valid_update_data["name"])
        self.assertEqual(gwc.short_name, self.valid_update_data["short_name"])
        self.assertEqual(gwc.place, self.valid_update_data["place"])
        self.assertEqual(gwc.main_class.pk, self.valid_update_data["main_class"])
        self.assertEqual(gwc.eas.pk, self.valid_update_data["eas"])

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_update_data)
        self.assertRedirects(response, self.redirect_url)


class GWCDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.stand = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.means_of_labor,
        )

        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None
        )

        cls.gwc = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=100)
        )

        cls.url = reverse("route_tech:delete_gwc", args=[cls.gwc.pk])
        cls.redirect_url = reverse("classes:index")

    def test_uses_gwc_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/gwc/gwc.html")

    def test_renders_information_about_removable_object(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.gwc.pk)
        self.assertContains(response, self.gwc.name)
        self.assertContains(response, self.gwc.short_name)
        self.assertContains(response, self.gwc.main_class.name)
        self.assertContains(response, self.gwc.eas.name)
        self.assertContains(response, self.gwc.place)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url)
        self.assertEqual(GroupWorkingCenter.objects.count(), 0)

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class ProdOperationCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.ei = Ei.objects.first()
        cls.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")

        cls.prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.product_class,
            image=cls.image,
            cost=Decimal('100.00'),
            ei=cls.ei,
            modification=None,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.stand = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.means_of_labor,
        )
        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None,
        )
        cls.center = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=100),
        )

        cls.valid_num_of_workers = cls.faker.random_int(min=1, max=10)
        cls.valid_t_pz = cls.faker.random_number(digits=2)
        cls.valid_t_sht = cls.faker.random_number(digits=2)

        cls.valid_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.valid_num_of_workers,
            "t_pz": cls.valid_t_pz,
            "t_sht": cls.valid_t_sht,
        }

        cls.empty_prod_data = {
            "prod": "",
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.valid_num_of_workers,
            "t_pz": cls.valid_t_pz,
            "t_sht": cls.valid_t_sht,
        }

        cls.empty_tech_oper_data = {
            "prod": cls.prod.pk,
            "tech_oper": "",
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.valid_num_of_workers,
            "t_pz": cls.valid_t_pz,
            "t_sht": cls.valid_t_sht,
        }

        cls.empty_profession_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": "",
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.valid_num_of_workers,
            "t_pz": cls.valid_t_pz,
            "t_sht": cls.valid_t_sht,
        }

        cls.empty_center_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": "",
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.valid_num_of_workers,
            "t_pz": cls.valid_t_pz,
            "t_sht": cls.valid_t_sht,
        }

        cls.empty_qualification_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": "",
            "num_of_workers": cls.valid_num_of_workers,
            "t_pz": cls.valid_t_pz,
            "t_sht": cls.valid_t_sht,
        }

        cls.invalid_num_of_workers_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": 0,
            "t_pz": cls.valid_t_pz,
            "t_sht": cls.valid_t_sht,
        }

        cls.url = reverse("route_tech:add_prod_operation")
        cls.redirect_url = reverse("classes:index")

    def test_uses_prod_operation_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/prod_operation/prod_operation.html")

    def test_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url, self.valid_data)
        instance = ProdOperation.objects.last()
        self.assertIsNotNone(instance.pk)
        self.assertEqual(instance.prod.pk, self.valid_data["prod"])
        self.assertEqual(instance.tech_oper.pk, self.valid_data["tech_oper"])
        self.assertEqual(instance.profession.pk, self.valid_data["profession"])
        self.assertEqual(instance.center.pk, self.valid_data["center"])
        self.assertEqual(instance.qualification.pk, self.valid_data["qualification"])
        self.assertEqual(instance.t_pz, self.valid_data["t_pz"])
        self.assertEqual(instance.t_sht, self.valid_data["t_sht"])
        self.assertEqual(instance.num_of_workers, self.valid_data["num_of_workers"])

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_prod_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_prod_data)
        self.assertContains(response, ProdOperErrors.EMPTY_PROD)

    def test_empty_tech_oper_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_tech_oper_data)
        self.assertContains(response, ProdOperErrors.EMPTY_TECH_OPER)

    def test_empty_profession_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_profession_data)
        self.assertContains(response, ProdOperErrors.EMPTY_PROFESSION)

    def test_empty_center_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_center_data)
        self.assertContains(response, ProdOperErrors.EMPTY_CENTER)

    def test_empty_qualification_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_qualification_data)
        self.assertContains(response, ProdOperErrors.EMPTY_QUALIFICATION)

    def test_invalid_num_of_workers_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.invalid_num_of_workers_data)
        self.assertContains(response, ProdOperErrors.INVALID_NUM_OF_WORKERS)


class ProdOperationDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.ei = Ei.objects.first()
        cls.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")

        cls.prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.product_class,
            image=cls.image,
            cost=Decimal('100.00'),
            ei=cls.ei,
            modification=None,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.stand = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.means_of_labor,
        )
        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None,
        )
        cls.center = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=100),
        )

        cls.prod_operation = ProdOperation.objects.create(
            prod=cls.prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=cls.faker.random_int(min=1, max=10),
            t_pz=cls.faker.random_number(digits=2),
            t_sht=cls.faker.random_number(digits=2),
        )

        cls.url = reverse("route_tech:delete_prod_operation", args=[cls.prod_operation.pk])
        cls.redirect_url = reverse("classes:index")

    def test_uses_prod_operation_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/prod_operation/prod_operation.html")

    def test_renders_information_about_removable_object(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.prod_operation.pk)
        self.assertContains(response, self.prod_operation.prod.name)
        self.assertContains(response, self.prod_operation.tech_oper.name)
        self.assertContains(response, self.prod_operation.profession.name)
        self.assertContains(response, self.prod_operation.center.name)
        self.assertContains(response, self.prod_operation.qualification.name)
        self.assertContains(response, self.prod_operation.num_of_workers)
        self.assertContains(response, self.prod_operation.t_pz)
        self.assertContains(response, self.prod_operation.t_sht)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url)
        self.assertEqual(ProdOperation.objects.count(), 0)

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class ProdOperationUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.ei = Ei.objects.first()
        cls.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")

        cls.prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.product_class,
            image=cls.image,
            cost=Decimal('100.00'),
            ei=cls.ei,
            modification=None,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.stand = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.means_of_labor,
        )
        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None,
        )
        cls.center = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=100),
        )

        cls.prod_operation = ProdOperation.objects.create(
            prod=cls.prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=cls.faker.random_int(min=1, max=10),
            t_pz=cls.faker.random_number(digits=2),
            t_sht=cls.faker.random_number(digits=2),
        )

        cls.new_prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.product_class,
            image=cls.image,
            cost=Decimal('200.00'),
            ei=cls.ei,
            modification=None,
        )
        cls.new_tech_oper = ClassStruct.objects.get(pk=OperationConsts.STAMPING)
        cls.new_profession = ClassStruct.objects.get(pk=ProfessionConsts.PRESSMAN)
        cls.new_center = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=100),
        )
        cls.new_qualification = ClassStruct.objects.get(pk=QualificationConsts.SECOND_RANK)
        cls.new_num_of_workers = cls.faker.random_int(min=2, max=20)
        cls.new_t_pz = cls.faker.random_number(digits=3)
        cls.new_t_sht = cls.faker.random_number(digits=3)

        cls.valid_update_data = {
            "prod": cls.new_prod.pk,
            "tech_oper": cls.new_tech_oper.pk,
            "profession": cls.new_profession.pk,
            "center": cls.new_center.pk,
            "qualification": cls.new_qualification.pk,
            "num_of_workers": cls.new_num_of_workers,
            "t_pz": cls.new_t_pz,
            "t_sht": cls.new_t_sht,
        }

        cls.url = reverse("route_tech:edit_prod_operation", args=[cls.prod_operation.pk])
        cls.redirect_url = reverse("route_tech:detail_prod_operation", args=[cls.prod_operation.pk])

    def test_uses_prod_operation_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/prod_operation/prod_operation.html")

    def test_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url, self.valid_update_data)
        prod_oper = ProdOperation.objects.last()
        self.assertEqual(prod_oper.prod.pk, self.valid_update_data["prod"])
        self.assertEqual(prod_oper.tech_oper.pk, self.valid_update_data["tech_oper"])
        self.assertEqual(prod_oper.profession.pk, self.valid_update_data["profession"])
        self.assertEqual(prod_oper.center.pk, self.valid_update_data["center"])
        self.assertEqual(prod_oper.qualification.pk, self.valid_update_data["qualification"])
        self.assertEqual(prod_oper.num_of_workers, self.valid_update_data["num_of_workers"])
        self.assertEqual(prod_oper.t_pz, self.valid_update_data["t_pz"])
        self.assertEqual(prod_oper.t_sht, self.valid_update_data["t_sht"])

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_update_data)
        self.assertRedirects(response, self.redirect_url)


class EditTechnologicalRoutePositionsViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class,
        )

        cls.ei = Ei.objects.first()
        cls.image = SimpleUploadedFile("test.jpg", b"content", content_type="image/jpeg")

        cls.prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.product_class,
            image=cls.image,
            cost=Decimal('100.00'),
            ei=cls.ei,
            modification=None,
        )
        cls.output_prod = Prod.objects.create(
            name=cls.faker.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.product_class,
            image=cls.image,
            cost=Decimal('200.00'),
            ei=cls.ei,
            modification=None,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.stand = ClassStruct.objects.create(
            name=cls.faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.means_of_labor,
        )
        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None,
        )
        cls.center = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=100),
        )

        cls.parent_prod_oper = ProdOperation.objects.create(
            prod=cls.prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=cls.faker.random_int(min=1, max=10),
            t_pz=cls.faker.random_number(digits=2),
            t_sht=cls.faker.random_number(digits=2),
        )

        cls.output_prod_oper1 = ProdOperation.objects.create(
            prod=cls.output_prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=cls.faker.random_int(min=1, max=10),
            t_pz=cls.faker.random_number(digits=2),
            t_sht=cls.faker.random_number(digits=2),
        )
        cls.output_prod_oper2 = ProdOperation.objects.create(
            prod=cls.output_prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=cls.faker.random_int(min=1, max=10),
            t_pz=cls.faker.random_number(digits=2),
            t_sht=cls.faker.random_number(digits=2),
        )

        cls.existing_pos1 = ProdOperationPos.objects.create(
            input_prod_oper=cls.parent_prod_oper,
            output_prod_oper=cls.output_prod_oper1,
            input_quantity=Decimal('1.5'),
            output_quantity=Decimal('2.0'),
        )
        cls.existing_pos2 = ProdOperationPos.objects.create(
            input_prod_oper=cls.parent_prod_oper,
            output_prod_oper=cls.output_prod_oper2,
            input_quantity=Decimal('3.0'),
            output_quantity=Decimal('4.0'),
        )

        cls.prefix_name = ProdOperationPosFormSet.get_default_prefix()

        cls.create_valid_forms_data = [
            {
                "id": cls.existing_pos1.pk,
                "output_prod_oper": cls.output_prod_oper1.pk,
                "input_quantity": "1.5",
                "output_quantity": "2.0",
                "DELETE": "",
            },
            {
                "id": "",
                "output_prod_oper": cls.output_prod_oper2.pk,
                "input_quantity": "5.5",
                "output_quantity": "6.5",
                "DELETE": "",
            },
        ]

        cls.delete_forms_data = [
            {
                "id": cls.existing_pos1.pk,
                "output_prod_oper": cls.output_prod_oper1.pk,
                "input_quantity": "1.5",
                "output_quantity": "2.0",
                "DELETE": "on",
            },
        ]

        cls.update_forms_data = [
            {
                "id": cls.existing_pos1.pk,
                "output_prod_oper": cls.output_prod_oper2.pk,
                "input_quantity": "99.9",
                "output_quantity": "88.8",
                "DELETE": "",
            },
        ]

        cls.empty_output_prod_oper_forms_data = [
            {
                "id": cls.existing_pos1.pk,
                "output_prod_oper": "",
                "input_quantity": "1.5",
                "output_quantity": "2.0",
                "DELETE": "",
            },
        ]

        cls.invalid_input_quantity_forms_data = [
            {
                "id": cls.existing_pos1.pk,
                "output_prod_oper": cls.output_prod_oper1.pk,
                "input_quantity": "-1.0",
                "output_quantity": "2.0",
                "DELETE": "",
            },
        ]

        cls.invalid_output_quantity_forms_data = [
            {
                "id": cls.existing_pos1.pk,
                "output_prod_oper": cls.output_prod_oper1.pk,
                "input_quantity": "1.5",
                "output_quantity": "-2.0",
                "DELETE": "",
            },
        ]

        cls.empty_input_quantity_forms_data = [
            {
                "id": cls.existing_pos1.pk,
                "output_prod_oper": cls.output_prod_oper1.pk,
                "input_quantity": "",
                "output_quantity": "2.0",
                "DELETE": "",
            },
        ]

        cls.empty_output_quantity_forms_data = [
            {
                "id": cls.existing_pos1.pk,
                "output_prod_oper": cls.output_prod_oper1.pk,
                "input_quantity": "1.5",
                "output_quantity": "",
                "DELETE": "",
            },
        ]

        cls.allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)

        cls.email = cls.faker.email()[:UserConsts.EMAIL_MAX_LENGTH]
        cls.password = "StrongPass123!"
        cls.first_name = cls.faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH]
        cls.middle_name = cls.faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH]
        cls.last_name = cls.faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH]
        cls.phone_number = "+7 (999) 123-45-67"

        cls.allowed_user = User.objects.create_user(
            email=cls.email,
            first_name=cls.first_name,
            middle_name=cls.middle_name,
            last_name=cls.last_name,
            phone_number=cls.phone_number,
            password=cls.password,
            role=cls.allowed_role,
        )

        cls.url = reverse("route_tech:edit_prod_operation_pos", args=[cls.prod.pk])
        cls.redirect_url = reverse("products:detail", args=[cls.prod.pk])

    def _get_form_data(self, total_forms, initial_forms, forms_data):
        data = {
            f'{self.prefix_name}-TOTAL_FORMS': total_forms,
            f'{self.prefix_name}-INITIAL_FORMS': initial_forms,
            f'{self.prefix_name}-MIN_NUM_FORMS': 0,
            f'{self.prefix_name}-MAX_NUM_FORMS': 1000,
        }
        for idx, form_data in enumerate(forms_data):
            for key, value in form_data.items():
                data[f'{self.prefix_name}-{idx}-{key}'] = value
        return data

    def test_uses_edit_positions_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/prodoperation_pos_edit.html")

    def test_renders_formset(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("formset", response.context)

    def test_has_edit_mode_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("edit_mode", response.context)

    def test_edit_mode_is_true(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url, data={"edit": "1"})
        self.assertEqual(response.context.get("edit_mode"), True)

    def test_edit_mode_is_false(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertEqual(response.context.get("edit_mode"), False)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        data = self._get_form_data(
            total_forms=len(self.create_valid_forms_data),
            initial_forms=1,
            forms_data=self.create_valid_forms_data,
        )
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # существующая позиция не удалена
        self.assertTrue(
            ProdOperationPos.objects.filter(pk=self.existing_pos1.pk).exists()
        )
        # новая позиция создана
        self.assertTrue(
            ProdOperationPos.objects.filter(
                input_prod_oper=self.parent_prod_oper,
                output_prod_oper=self.output_prod_oper2,
                input_quantity=Decimal("5.5"),
                output_quantity=Decimal("6.5"),
            ).exists()
        )

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        data = self._get_form_data(
            total_forms=len(self.create_valid_forms_data),
            initial_forms=1,
            forms_data=self.create_valid_forms_data,
        )
        response = self.client.post(self.url, data=data)
        self.assertRedirects(response, self.redirect_url)

    def test_can_add_new_position(self):
        self.client.force_login(self.allowed_user)
        initial_count = ProdOperationPos.objects.filter(
            input_prod_oper=self.parent_prod_oper
        ).count()

        new_form = [
            {
                "id": "",
                "output_prod_oper": self.output_prod_oper2.pk,
                "input_quantity": "5.5",
                "output_quantity": "6.5",
                "DELETE": "",
            },
        ]
        data = self._get_form_data(
            total_forms=1,
            initial_forms=0,
            forms_data=new_form,
        )
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            ProdOperationPos.objects.filter(
                input_prod_oper=self.parent_prod_oper
            ).count(),
            initial_count + 1,
        )
        self.assertTrue(
            ProdOperationPos.objects.filter(
                input_prod_oper=self.parent_prod_oper,
                output_prod_oper=self.output_prod_oper2,
                input_quantity=Decimal("5.5"),
                output_quantity=Decimal("6.5"),
            ).exists()
        )

    def test_can_update_existing_positions(self):
        self.client.force_login(self.allowed_user)
        data = self._get_form_data(
            total_forms=len(self.update_forms_data),
            initial_forms=1,
            forms_data=self.update_forms_data,
        )
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.existing_pos1.refresh_from_db()
        self.assertEqual(self.existing_pos1.input_quantity, Decimal("99.9"))
        self.assertEqual(self.existing_pos1.output_quantity, Decimal("88.8"))
        self.assertEqual(
            self.existing_pos1.output_prod_oper, self.output_prod_oper2
        )

    def test_can_delete_existing_positions(self):
        self.client.force_login(self.allowed_user)
        data = self._get_form_data(
            total_forms=len(self.delete_forms_data),
            initial_forms=1,
            forms_data=self.delete_forms_data,
        )
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(
            ProdOperationPos.objects.filter(pk=self.existing_pos1.pk).exists()
        )
