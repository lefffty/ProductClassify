from django.urls import reverse
from django.utils.html import escape
from django.contrib.auth import get_user_model

from decimal import Decimal
from http import HTTPStatus

from classes.models import ClassStruct
from classes.constants import (
    MetaConsts,
    ProductsConsts,
    OperationConsts,
    ProfessionConsts,
    QualificationConsts,
)

from accounts.constants import RoleCodes
from accounts.models import Role

from ei.models import Ei

from tests.unit.accounts.factories.user import UserFactory
from tests.unit.classes.factories.class_struct import ClassStructFactory
from tests.unit.products.factories.product import ProdFactory
from tests.unit.route_tech.factories.eas import EASFactory, EASFormData
from tests.unit.route_tech.factories.gwc import GWCFactory, GWCFormData
from tests.unit.route_tech.factories.prod_oper import ProdOperationFactory, ProdOperationFormData
from tests.unit.route_tech.factories.prod_oper_pos import ProdOperationPosFactory

from route_tech.models import EconomicActivitySubject, GroupWorkingCenter, ProdOperation, ProdOperationPos
from route_tech.forms import ProdOperationPosFormSet
from route_tech.errors import EASErrors, GWCErrors, ProdOperErrors

from tests.unit.base import BaseUnitTestCase

User = get_user_model()


class EASCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.parent_subject = EASFactory(main_class=cls.enterprise)

        cls.valid_data = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject="",
        )
        cls.valid_data_with_parent = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=cls.parent_subject.pk,
        )
        cls.empty_name_data = EASFormData(
            name="",
            main_class=cls.enterprise.pk,
            main_subject="",
        )
        cls.empty_short_name_data = EASFormData(
            short_name="",
            main_class=cls.enterprise.pk,
            main_subject="",
        )
        cls.empty_main_class_data = EASFormData(
            main_class="",
            main_subject="",
        )

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
        self.assertEqual(eas.name, self.valid_data_with_parent["name"])
        self.assertEqual(eas.short_name, self.valid_data_with_parent["short_name"])
        self.assertEqual(eas.main_class.pk, self.valid_data_with_parent["main_class"])
        self.assertIsNotNone(eas.main_subject.pk)

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_data)
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
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)

        cls.parent_subject = EASFactory(main_class=cls.enterprise)
        cls.subject = EASFactory(
            main_class=cls.enterprise,
            main_subject=cls.parent_subject,
        )

        cls.valid_update_data = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=cls.parent_subject.pk,
        )

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
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.name, self.valid_update_data["name"])
        self.assertEqual(self.subject.short_name, self.valid_update_data["short_name"])
        self.assertEqual(self.subject.main_class.pk, MetaConsts.ENTERPRISE)
        self.assertEqual(self.subject.main_subject.pk, self.parent_subject.pk)

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_update_data)
        self.assertRedirects(response, self.redirect_url)


class EASDetailViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)

        cls.parent_subject = EASFactory(main_class=cls.enterprise)
        cls.subject = EASFactory(
            main_class=cls.enterprise,
            main_subject=cls.parent_subject,
        )

        cls.url = reverse("route_tech:detail_eas", args=[cls.subject.pk])

    def test_uses_eas_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "route_tech/eas/detail.html")

    def test_renders_correct_information(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.subject.name)
        self.assertContains(response, self.subject.short_name)
        self.assertContains(response, self.subject.main_subject.name)
        for child in self.subject.children.all():
            self.assertContains(response, child.name)
            self.assertContains(response, child.short_name)


class EASDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.subject = EASFactory(main_class=cls.enterprise)

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
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.stand = ClassStructFactory(
            main_class=cls.means_of_labor,
        )
        cls.eas = EASFactory(main_class=cls.enterprise)

        cls.valid_data = GWCFormData(
            main_class=cls.stand.pk,
            eas=cls.eas.pk,
            place=42,
        )
        cls.empty_name_data = GWCFormData(
            name="",
            main_class=cls.stand.pk,
            eas=cls.eas.pk,
            place=42,
        )
        cls.empty_short_name_data = GWCFormData(
            short_name="",
            main_class=cls.stand.pk,
            eas=cls.eas.pk,
            place=42,
        )
        cls.empty_main_class_data = GWCFormData(
            main_class="",
            eas=cls.eas.pk,
            place=42,
        )
        cls.empty_eas_data = GWCFormData(
            main_class=cls.stand.pk,
            eas="",
            place=42,
        )
        cls.empty_place_data = GWCFormData(
            main_class=cls.stand.pk,
            eas=cls.eas.pk,
            place="",
        )
        cls.invalid_place_data = GWCFormData(
            main_class=cls.stand.pk,
            eas=cls.eas.pk,
            place=-1,
        )

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
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.stand = ClassStructFactory(main_class=cls.means_of_labor)
        cls.eas = EASFactory(main_class=cls.enterprise)

        cls.gwc = GWCFactory(
            main_class=cls.stand,
            eas=cls.eas,
            place=42,
        )

        cls.valid_update_data = GWCFormData(
            main_class=cls.stand.pk,
            eas=cls.eas.pk,
            place=84,
        )

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
        self.gwc.refresh_from_db()
        self.assertEqual(self.gwc.name, self.valid_update_data["name"])
        self.assertEqual(self.gwc.short_name, self.valid_update_data["short_name"])
        self.assertEqual(self.gwc.place, self.valid_update_data["place"])
        self.assertEqual(self.gwc.main_class.pk, self.valid_update_data["main_class"])
        self.assertEqual(self.gwc.eas.pk, self.valid_update_data["eas"])

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_update_data)
        self.assertRedirects(response, self.redirect_url)


class GWCDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.stand = ClassStructFactory(main_class=cls.means_of_labor)
        cls.eas = EASFactory(main_class=cls.enterprise)

        cls.gwc = GWCFactory(
            main_class=cls.stand,
            eas=cls.eas,
            place=42,
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
        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStructFactory(main_class=cls.nuts_class)
        cls.ei = Ei.objects.first()

        cls.prod = ProdFactory(
            class_field=cls.product_class,
            image=None,
            cost=Decimal("100.00"),
            ei=cls.ei,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.stand = ClassStructFactory(main_class=cls.means_of_labor)
        cls.eas = EASFactory(main_class=cls.enterprise)
        cls.center = GWCFactory(
            main_class=cls.stand,
            eas=cls.eas,
            place=42,
        )

        cls.valid_data = ProdOperationFormData(
            prod=cls.prod.pk,
            tech_oper=cls.tech_oper.pk,
            profession=cls.profession.pk,
            center=cls.center.pk,
            qualification=cls.qualification.pk,
            num_of_workers=3,
            t_pz=1.0,
            t_sht=2.0,
        )
        cls.empty_prod_data = ProdOperationFormData(
            prod="", tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=3, t_pz=1.0, t_sht=2.0,
        )
        cls.empty_tech_oper_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper="", profession=cls.profession.pk,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=3, t_pz=1.0, t_sht=2.0,
        )
        cls.empty_profession_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession="",
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=3, t_pz=1.0, t_sht=2.0,
        )
        cls.empty_center_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center="", qualification=cls.qualification.pk,
            num_of_workers=3, t_pz=1.0, t_sht=2.0,
        )
        cls.empty_qualification_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=cls.center.pk, qualification="",
            num_of_workers=3, t_pz=1.0, t_sht=2.0,
        )
        cls.invalid_num_of_workers_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=0, t_pz=1.0, t_sht=2.0,
        )

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
        self.assertEqual(instance.num_of_workers, self.valid_data["num_of_workers"])
        self.assertEqual(instance.t_pz, self.valid_data["t_pz"])
        self.assertEqual(instance.t_sht, self.valid_data["t_sht"])

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
        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStructFactory(main_class=cls.nuts_class)
        cls.ei = Ei.objects.first()

        cls.prod = ProdFactory(
            class_field=cls.product_class,
            image=None,
            cost=Decimal("100.00"),
            ei=cls.ei,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.stand = ClassStructFactory(main_class=cls.means_of_labor)
        cls.eas = EASFactory(main_class=cls.enterprise)
        cls.center = GWCFactory(
            main_class=cls.stand,
            eas=cls.eas,
            place=42,
        )

        cls.prod_operation = ProdOperationFactory(
            prod=cls.prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=3,
            t_pz=1.0,
            t_sht=2.0,
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

    def test_can_save_a_POST_request(self):
        self.client.post(self.url)
        self.assertEqual(ProdOperation.objects.count(), 0)

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class ProdOperationUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStructFactory(main_class=cls.nuts_class)
        cls.ei = Ei.objects.first()

        cls.prod = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("100.00"), ei=cls.ei,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.stand = ClassStructFactory(main_class=cls.means_of_labor)
        cls.eas = EASFactory(main_class=cls.enterprise)
        cls.center = GWCFactory(main_class=cls.stand, eas=cls.eas, place=42)

        cls.prod_operation = ProdOperationFactory(
            prod=cls.prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=3,
            t_pz=1.0,
            t_sht=2.0,
        )

        cls.new_prod = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("200.00"), ei=cls.ei,
        )
        cls.new_tech_oper = ClassStruct.objects.get(pk=OperationConsts.STAMPING)
        cls.new_profession = ClassStruct.objects.get(pk=ProfessionConsts.PRESSMAN)
        cls.new_center = GWCFactory(main_class=cls.stand, eas=cls.eas, place=43)
        cls.new_qualification = ClassStruct.objects.get(pk=QualificationConsts.SECOND_RANK)

        cls.valid_update_data = ProdOperationFormData(
            prod=cls.new_prod.pk,
            tech_oper=cls.new_tech_oper.pk,
            profession=cls.new_profession.pk,
            center=cls.new_center.pk,
            qualification=cls.new_qualification.pk,
            num_of_workers=5,
            t_pz=3.0,
            t_sht=4.0,
        )

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
        self.prod_operation.refresh_from_db()
        self.assertEqual(self.prod_operation.prod.pk, self.valid_update_data["prod"])
        self.assertEqual(self.prod_operation.tech_oper.pk, self.valid_update_data["tech_oper"])
        self.assertEqual(self.prod_operation.profession.pk, self.valid_update_data["profession"])
        self.assertEqual(self.prod_operation.center.pk, self.valid_update_data["center"])
        self.assertEqual(self.prod_operation.qualification.pk, self.valid_update_data["qualification"])
        self.assertEqual(self.prod_operation.num_of_workers, self.valid_update_data["num_of_workers"])
        self.assertEqual(self.prod_operation.t_pz, self.valid_update_data["t_pz"])
        self.assertEqual(self.prod_operation.t_sht, self.valid_update_data["t_sht"])

    def test_redirects_after_POST_request(self):
        response = self.client.post(self.url, self.valid_update_data)
        self.assertRedirects(response, self.redirect_url)


class EditTechnologicalRoutePositionsViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStructFactory(main_class=cls.nuts_class)

        cls.ei = Ei.objects.first()

        cls.prod = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("100.00"), ei=cls.ei,
        )
        cls.output_prod = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("200.00"), ei=cls.ei,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.stand = ClassStructFactory(main_class=cls.means_of_labor)
        cls.eas = EASFactory(main_class=cls.enterprise)
        cls.center = GWCFactory(main_class=cls.stand, eas=cls.eas, place=42)

        cls.parent_prod_oper = ProdOperationFactory(
            prod=cls.prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
        )
        cls.output_prod_oper1 = ProdOperationFactory(
            prod=cls.output_prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
        )
        cls.output_prod_oper2 = ProdOperationFactory(
            prod=cls.output_prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
        )

        cls.existing_pos1 = ProdOperationPosFactory(
            input_prod_oper=cls.parent_prod_oper,
            output_prod_oper=cls.output_prod_oper1,
            input_quantity=Decimal("1.5"),
            output_quantity=Decimal("2.0"),
        )
        cls.existing_pos2 = ProdOperationPosFactory(
            input_prod_oper=cls.parent_prod_oper,
            output_prod_oper=cls.output_prod_oper2,
            input_quantity=Decimal("3.0"),
            output_quantity=Decimal("4.0"),
        )

        cls.prefix_name = ProdOperationPosFormSet.get_default_prefix()

        cls.create_valid_forms_data = [
            {"id": cls.existing_pos1.pk, "output_prod_oper": cls.output_prod_oper1.pk,
             "input_quantity": "1.5", "output_quantity": "2.0", "DELETE": ""},
            {"id": "", "output_prod_oper": cls.output_prod_oper2.pk,
             "input_quantity": "5.5", "output_quantity": "6.5", "DELETE": ""},
        ]
        cls.delete_forms_data = [
            {"id": cls.existing_pos1.pk, "output_prod_oper": cls.output_prod_oper1.pk,
             "input_quantity": "1.5", "output_quantity": "2.0", "DELETE": "on"},
        ]
        cls.update_forms_data = [
            {"id": cls.existing_pos1.pk, "output_prod_oper": cls.output_prod_oper2.pk,
             "input_quantity": "99.9", "output_quantity": "88.8", "DELETE": ""},
        ]
        cls.empty_output_prod_oper_forms_data = [
            {"id": cls.existing_pos1.pk, "output_prod_oper": "",
             "input_quantity": "1.5", "output_quantity": "2.0", "DELETE": ""},
        ]
        cls.invalid_input_quantity_forms_data = [
            {"id": cls.existing_pos1.pk, "output_prod_oper": cls.output_prod_oper1.pk,
             "input_quantity": "-1.0", "output_quantity": "2.0", "DELETE": ""},
        ]
        cls.invalid_output_quantity_forms_data = [
            {"id": cls.existing_pos1.pk, "output_prod_oper": cls.output_prod_oper1.pk,
             "input_quantity": "1.5", "output_quantity": "-2.0", "DELETE": ""},
        ]
        cls.empty_input_quantity_forms_data = [
            {"id": cls.existing_pos1.pk, "output_prod_oper": cls.output_prod_oper1.pk,
             "input_quantity": "", "output_quantity": "2.0", "DELETE": ""},
        ]
        cls.empty_output_quantity_forms_data = [
            {"id": cls.existing_pos1.pk, "output_prod_oper": cls.output_prod_oper1.pk,
             "input_quantity": "1.5", "output_quantity": "", "DELETE": ""},
        ]

        cls.allowed_role = Role.objects.get(code=RoleCodes.TECHNOLOGIST)
        cls.allowed_user = UserFactory(role=cls.allowed_role)

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
