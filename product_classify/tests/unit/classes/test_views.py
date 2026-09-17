from django.utils.html import escape
from django.urls import reverse
from django.contrib.auth import get_user_model

from http import HTTPStatus
from parameterized import parameterized
from unittest.mock import patch

from tests.unit.base import BaseUnitTestCase
from tests.unit.accounts.factories.user import UserFactory
from tests.unit.parametr.factories.parametr import ParametrFactory
from tests.unit.products.factories.product import ProdFactory
from tests.unit.products.factories.par_prod import ParProdFactory
from tests.unit.classes.factories.parclass import ParClassFormData, ParClassFactory, ChangeParClassFormData
from tests.unit.classes.factories.class_struct import (
    ClassFormData,
    ProdClassFormData,
    EnumsClassFormData,
    ClassStructFactory,
)

from accounts.models import Role
from accounts.constants import RoleCodes

from parametr.models import Parametr
from parametr.constants import ParametrConsts

from products.models import Prod
from products.models import ParProd

from ei.models import Ei
from ei.constants import KILOGRAM_ID

from classes.models import ClassStruct, ParClass
from classes.forms import ProdClassForm, EnumClassForm
from classes.errors import (
    ChangeParClassErrors,
    ClassStructErrors,
    ParClassErrors, 
)
from classes.constants import (
    OperationConsts,
    ProdClassConsts,
    ProductsConsts,
    MetaConsts,
    EnumsIds,
    ParamIds,
    NUMERIC_PARAMS
)

User = get_user_model()


class MainPageTemplateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reversed_url = reverse("classes:index")

    def test_main_page_template_view_uses_index_template(self):
        response = self.client.get(self.reversed_url)
        self.assertTemplateUsed(response, "classes/index.html")

    def test_fastener_classes_are_in_context(self):
        response = self.client.get(self.reversed_url)
        self.assertIn("fastener_classes", response.context)

    def test_fastener_classes_count_is_correct(self):
        response = self.client.get(self.reversed_url)
        self.assertEqual(len(response.context["fastener_classes"]), 3)

    def test_renders_nav_bar(self):
        response = self.client.get(self.reversed_url)
        self.assertContains(response, '<nav class="navbar">')


class CategoryClassesListViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        nuts_class = ClassStruct.objects.get(pk=3)

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        ClassStructFactory(main_class=nuts_class)

    def test_returns_302_for_anonymous_user(self):
        url = reverse("classes:category_classes", kwargs={"class_id": 3})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_returns_403_for_authenticated_user(self):
        url = reverse("classes:category_classes", kwargs={"class_id": 3})
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        url = reverse("classes:category_classes", kwargs={"class_id": 3})
        self.client.force_login(self.allowed_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.expand([
        (3,),
        (4,),
        (5,),
    ])
    def test_category_classes_view_returns_ok_status_code(self, class_id):
        self.client.force_login(self.allowed_user)
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.expand([
        (3,),
        (4,),
        (5,),
    ])
    def test_category_classes_view_uses_category_template(self, class_id):
        self.client.force_login(self.allowed_user)
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertTemplateUsed(response, "classes/category.html")

    @parameterized.expand([
        (3, 1),
        (4, 0),
        (5, 0),
    ])
    def test_displays_correct_number_of_subclasses(self, class_id, expected_count):
        self.client.force_login(self.allowed_user)
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertEqual(len(response.context["classes"]), expected_count)

    def test_returns_not_found_error_if_given_class_id_is_invalid(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 6}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        
    def test_fastener_classes_are_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 3}))
        self.assertIn("fastener_classes", response.context)

    def test_main_class_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 3}))
        self.assertIn("main_class", response.context)


class ProdClassCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.data = ProdClassFormData(
            base_ei="",
            main_class=cls.nuts_class.pk,
        )
        cls.invalid_data = ProdClassFormData(
            short_name="",
            base_ei="",
            main_class="",
        )
        cls.empty_main_class_data = ProdClassFormData(
            short_name="",
            base_ei="",
            main_class="",
        )
        cls.empty_name_data = ProdClassFormData(
            name="",
            short_name="",
            base_ei="",
            main_class=cls.nuts_class.pk,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:add_prod_class")
        cls.redirect_url = reverse("classes:index")

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

    def test_uses_prod_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_renders_create_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=self.url,
            data=self.data,
        )
        new_class = ClassStruct.objects.last()
        self.assertEqual(ClassStruct.objects.count(), count_before + 1)
        self.assertEqual(new_class.name, self.data["name"])
        self.assertEqual(new_class.short_name, self.data["short_name"])
        self.assertIsNone(new_class.base_ei)

    def test_redirects_after_POST(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.data,
        )
        self.assertRedirects(response, self.redirect_url)

    def test_for_invalid_input_renders_prod_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.invalid_data,
        )
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_invalid_prod_class_data_is_not_saved(self):
        self.client.force_login(self.allowed_user)
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=self.url,
            data=self.invalid_data,
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)

    def test_empty_main_class_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.empty_main_class_data,
        )
        self.assertContains(
            response,
            escape(ClassStructErrors.EMPTY_MAIN_CLASS_ERROR),
        )

    def test_empty_name_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.empty_name_data,
        )
        self.assertContains(
            response,
            escape(ClassStructErrors.EMPTY_NAME_ERROR),
        )


class EnumClassCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)

        cls.valid_data = EnumsClassFormData(
            main_class=cls.int_enum.pk,
        )
        cls.invalid_data = EnumsClassFormData(
            name="",
            short_name="",
            main_class="",
        )
        cls.empty_name_data = EnumsClassFormData(
            name="",
            main_class=cls.int_enum.pk,
        )
        cls.empty_main_class_data = EnumsClassFormData(
            main_class="",
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:add_enum_class")
        cls.redirect_url = reverse("classes:index")

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

    def test_uses_enum_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_render_enum_class_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=self.url,
            data=self.valid_data,
        )
        new_enum_class = ClassStruct.objects.last()
        self.assertEqual(ClassStruct.objects.count(), count_before + 1)
        self.assertEqual(new_enum_class.name, self.valid_data["name"])
        self.assertEqual(new_enum_class.short_name, self.valid_data["short_name"])
        self.assertEqual(new_enum_class.main_class.pk, self.valid_data["main_class"])

    def test_redirect_after_correct_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.valid_data,
        )
        self.assertRedirects(response, self.redirect_url)

    def test_renders_enum_class_template_for_invalid_input(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.invalid_data,
        )
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_empty_name_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.empty_name_data,
        )
        self.assertContains(response, escape(ClassStructErrors.EMPTY_NAME_ERROR))

    def test_empty_main_class_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=self.url,
            data=self.empty_main_class_data,
        )
        self.assertContains(response, escape(ClassStructErrors.EMPTY_MAIN_CLASS_ERROR))


class ClassUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum_class = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.base_ei = Ei.objects.get(pk=KILOGRAM_ID)

        cls.enum_class = ClassStructFactory(
            main_class=cls.int_enum_class,
        )
        cls.support_enum_class = ClassStructFactory(
            main_class=cls.enum_class,
        )

        cls.enum_class_edit_data = EnumsClassFormData(
            main_class=cls.int_enum_class.pk,
        )
        cls.invalid_enum_class_edit_data = EnumsClassFormData(
            main_class=cls.enum_class.pk,
        )

        cls.prod_class = ClassStructFactory(
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.support_prod_class = ClassStructFactory(
            base_ei=cls.base_ei,
            main_class=cls.prod_class,
        )

        cls.prod_class_edit_data = ProdClassFormData(
            base_ei=cls.base_ei.pk,
            main_class=cls.nuts_class.pk,
        )
        cls.invalid_prod_class_edit_data = ProdClassFormData(
            base_ei=cls.base_ei.pk,
            main_class=cls.prod_class.pk,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

    def test_returns_403_for_anonymous_user(self):
        response = self.client.get(reverse("classes:edit", args=[self.enum_class.pk]))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_403_for_authenticated_user(self):
        self.client.force_login(self.not_allowed_user)
        response = self.client.get(reverse("classes:edit", args=[self.enum_class.pk]))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_returns_200_for_authorized_user(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(reverse("classes:edit", args=[self.enum_class.pk]))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_uses_enum_class_template_for_enum_class(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
        )
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_uses_prod_class_template_for_prod_class(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
        )
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_renders_enum_class_form_for_enum_class(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
        )
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], EnumClassForm)

    def test_renders_prod_class_form_for_prod_class(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
        )
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], ProdClassForm)

    def test_can_save_a_POST_request_for_prod_class(self):
        self.client.force_login(self.allowed_user)
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
            data=self.prod_class_edit_data,
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)
        updated_instance = ClassStruct.objects.get(pk=self.prod_class.pk)
        self.assertEqual(updated_instance.name, self.prod_class_edit_data["name"])
        self.assertEqual(updated_instance.short_name, self.prod_class_edit_data["short_name"])
        self.assertEqual(updated_instance.main_class.pk, self.prod_class_edit_data["main_class"])
        self.assertEqual(updated_instance.base_ei.pk, self.prod_class_edit_data["base_ei"])

    def test_can_save_a_POST_request_for_enum_class(self):
        self.client.force_login(self.allowed_user)
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
            data=self.enum_class_edit_data,
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)
        updated_instance = ClassStruct.objects.get(pk=self.enum_class.pk)
        self.assertEqual(updated_instance.name, self.enum_class_edit_data["name"])
        self.assertEqual(updated_instance.short_name, self.enum_class_edit_data["short_name"])
        self.assertEqual(updated_instance.main_class.pk, self.enum_class_edit_data["main_class"])

    def test_redirects_after_correct_POST_request_for_prod_class(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
            data=self.prod_class_edit_data,
        )
        redirect_url = reverse(
            "classes:category_classes",
            args=[self.prod_class.main_class.pk],
        )
        self.assertRedirects(response, redirect_url)

    def test_redirects_after_correct_POST_request_for_enum_class(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
            data=self.enum_class_edit_data,
        )
        redirect_url = reverse(
            "classes:category_classes",
            args=[self.enum_class.main_class.pk],
        )
        self.assertRedirects(response, redirect_url)

    def test_detected_classificator_cycle_validation_error_is_shown_on_page_for_prod_class(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
            data=self.invalid_prod_class_edit_data,
        )
        self.assertContains(response, escape(ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR))

    def test_detected_classificator_cycle_validation_error_is_shown_on_page_for_enum_class(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
            data=self.invalid_enum_class_edit_data,
        )
        self.assertContains(response, escape(ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR))


class DeleteClassViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStructFactory(main_class=cls.nuts_class)
        cls.class_id = cls.nuts_subclass.pk

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:delete", args=[cls.class_id])
        cls.redirect_url = reverse("classes:category_classes", args=[cls.nuts_class.pk])

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

    def test_uses_enum_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(path=self.url)
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_fastener_classes_are_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(path=self.url)
        self.assertIn("fastener_classes", response.context)

    def test_instance_is_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(path=self.url)
        self.assertIn("instance", response.context)

    def test_correctly_deletes_given_class(self):
        self.client.force_login(self.allowed_user)
        self.client.post(path=self.url)
        self.assertEqual(ClassStruct.objects.filter(pk=self.nuts_subclass.pk).count(), 0)

    def test_redirects_after_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(path=self.url)
        self.assertRedirects(response, self.redirect_url, fetch_redirect_response=False)

    def test_delete_class_and_descendants_was_called_with_correct_arguments(self):
        self.client.force_login(self.allowed_user)
        with patch.object(
            ClassStruct,
            "delete_class_and_descendants"
        ) as mock_delete_class_and_descendants:
            self.client.post(path=self.url)
            mock_delete_class_and_descendants.assert_called_once()
            mock_delete_class_and_descendants.assert_called_with(self.class_id)


class ClassParamCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStructFactory(
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.int_param_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.int_enum_type = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei,
        )
        cls.par2 = ParametrFactory(
            parametr_type=cls.int_enum_type,
            par_ei=cls.base_ei,
        )
        cls.par3 = ParametrFactory(
            parametr_type=cls.agregat_type,
            par_ei=None,
        )

        cls.valid_enum_type_data = ParClassFormData(
            class_field=cls.nuts_subclass.pk,
            parametr=cls.par2.pk,
            min_value="",
            max_value="",
        )
        cls.valid_numeric_type_data = ParClassFormData(
            class_field=cls.nuts_subclass.pk,
            parametr=cls.par1.pk,
            min_value=5,
            max_value=100,
        )
        cls.empty_class_field_data = ParClassFormData(
            class_field="",
            parametr=cls.par2.pk,
            min_value="",
            max_value="",
        )
        cls.empty_parametr_field_data = ParClassFormData(
            class_field=cls.nuts_subclass.pk,
            parametr="",
            min_value="",
            max_value="",
        )
        cls.agregat_type_data = ParClassFormData(
            class_field=cls.nuts_subclass.pk,
            parametr=cls.par3.pk,
            min_value="",
            max_value="",
        )
        cls.mn_or_mx_specified_data = ParClassFormData(
            class_field=cls.nuts_subclass.pk,
            parametr=cls.par2.pk,
            min_value=5,
            max_value="",
        )
        cls.mn_gt_mx_data = ParClassFormData(
            class_field=cls.nuts_subclass.pk,
            parametr=cls.par1.pk,
            min_value=500,
            max_value=10,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:add_param", args=[cls.nuts_subclass.pk])
        cls.redirect_url = reverse("classes:params_list", args=[cls.nuts_subclass.pk])

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

    def test_uses_par_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/param_class.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_has_instance_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_can_save_a_POST_enum_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.valid_enum_type_data)
        pair = ParClass.objects.first()
        self.assertEqual(pair.class_field.pk, self.valid_enum_type_data["class_field"])
        self.assertEqual(pair.parametr.pk, self.valid_enum_type_data["parametr"])
        self.assertIsNone(pair.min_value)
        self.assertIsNone(pair.max_value)

    def test_correctly_calculates_num_field(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.valid_numeric_type_data)
        self.client.post(self.url, data=self.valid_enum_type_data)
        p1 = ParClass.objects.first()
        p2 = ParClass.objects.last()
        self.assertEqual(p1.class_field, p2.class_field)
        self.assertEqual(p1.num, 1)
        self.assertEqual(p2.num, 2)

    def test_can_save_a_POST_numeric_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.valid_numeric_type_data)
        pair = ParClass.objects.first()
        self.assertEqual(pair.class_field.pk, self.valid_numeric_type_data["class_field"])
        self.assertEqual(pair.parametr.pk, self.valid_numeric_type_data["parametr"])
        self.assertEqual(pair.min_value, self.valid_numeric_type_data["min_value"])
        self.assertEqual(pair.max_value, self.valid_numeric_type_data["max_value"])

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.valid_numeric_type_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_class_field_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.empty_class_field_data)
        self.assertContains(response, escape(ParClassErrors.EMPTY_CLASS_FIELD))

    def test_empty_parametr_field_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.empty_parametr_field_data)
        self.assertContains(response, escape(ParClassErrors.EMPTY_PAR_FIELD))

    def test_min_value_or_max_value_was_specified_for_enum_parametr_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.mn_or_mx_specified_data)
        self.assertContains(
            response,
            escape(ParClassErrors.ENUM_AGGREGATE_RANGE_ERROR.format(self.par2.name)),
        )

    def test_min_value_is_gt_max_value_for_numeric_param_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.mn_gt_mx_data)
        self.assertContains(response, escape(ParClassErrors.MIN_GE_MAX))


class ClassParamUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)

        cls.nuts_subclass = ClassStructFactory(
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )

        cls.int_param_type = ClassStruct.objects.get(pk=ParamIds.INT)

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei,
        )

        cls.parclass1 = ParClassFactory(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            min_value=5,
            max_value=15,
            num=1,
        )

        cls.valid_data = ParClassFormData(
            class_field=cls.nuts_subclass.pk,
            parametr=cls.par1.pk,
            min_value=15,
            max_value=25,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:edit_param", args=[cls.nuts_subclass.pk, cls.par1.pk])
        cls.redirect_url = reverse("classes:params_list", args=[cls.nuts_subclass.pk])

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

    def test_uses_param_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/param_class.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.valid_data)

        self.parclass1.refresh_from_db()
        self.assertEqual(self.parclass1.class_field.pk, self.valid_data["class_field"])
        self.assertEqual(self.parclass1.parametr.pk, self.valid_data["parametr"])
        self.assertEqual(self.parclass1.min_value, self.valid_data["min_value"])
        self.assertEqual(self.parclass1.max_value, self.valid_data["max_value"])

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.redirect_url)


class ClassParamDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)

        cls.nuts_subclass = ClassStructFactory(
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )

        cls.int_param_type = ClassStruct.objects.get(pk=ParamIds.INT)

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei,
        )

        cls.product = ProdFactory(
            class_field=cls.nuts_subclass,
            image=None,
        )

        cls.parclass1 = ParClassFactory(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            min_value=1,
            max_value=10,
            num=1,
        )

        cls.parprod = ParProdFactory(
            prod=cls.product,
            par=cls.par1,
            int_value=5,
            double_value=None,
            enum_val=None,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:delete_param", args=[cls.nuts_subclass.pk, cls.par1.pk])
        cls.redirect_url = reverse("classes:params_list", args=[cls.nuts_subclass.pk])

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

    def test_uses_param_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/param_class.html")

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.assertEqual(ParClass.objects.count(), 1)
        self.client.post(self.url)
        self.assertEqual(ParClass.objects.count(), 0)

    def test_cascadingly_delete_parprod_records(self):
        self.client.force_login(self.allowed_user)
        self.assertEqual(ParProd.objects.count(), 1)
        self.client.post(self.url)
        self.assertEqual(ParProd.objects.count(), 0)

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class ChangeNumViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)

        cls.nuts_subclass = ClassStructFactory(
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )

        cls.int_param_type = ClassStruct.objects.get(pk=ParamIds.INT)

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei,
        )
        cls.par2 = ParametrFactory(
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei,
        )

        cls.parclass1 = ParClassFactory(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            min_value=1,
            max_value=10,
            num=1,
        )
        cls.parclass2 = ParClassFactory(
            class_field=cls.nuts_subclass,
            parametr=cls.par2,
            min_value=1,
            max_value=10,
            num=2,
        )

        cls.valid_data = ChangeParClassFormData(
            cls_1=cls.parclass1.pk,
            cls_2=cls.parclass2.pk,
        )
        cls.empty_first_data = ChangeParClassFormData(
            cls_1="",
            cls_2=cls.parclass2.pk,
        )
        cls.empty_second_data = ChangeParClassFormData(
            cls_1=cls.parclass1.pk,
            cls_2="",
        )
        cls.equal_fields_data = ChangeParClassFormData(
            cls_1=cls.parclass1.pk,
            cls_2=cls.parclass1.pk,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:change_num", args=[cls.nuts_subclass.pk])
        cls.redirect_url = reverse("classes:params_list", args=[cls.nuts_subclass.pk])

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

    def test_uses_change_num_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/change_num.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, data=self.valid_data)
        self.parclass1.refresh_from_db()
        self.parclass2.refresh_from_db()
        self.assertEqual(self.parclass1.num, 2)
        self.assertEqual(self.parclass2.num, 1)

    def test_redirects_after_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_first_field_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.empty_first_data)
        self.assertContains(response, escape(ChangeParClassErrors.EMPTY_FIRST_PAR))

    def test_empty_second_field_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.empty_second_data)
        self.assertContains(response, escape(ChangeParClassErrors.EMPTY_SECOND_PAR))

    def test_equal_fields_validation_error_is_shown_on_page(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, data=self.equal_fields_data)
        self.assertContains(response, escape(ChangeParClassErrors.EQUAL_PAR))


class ClassParamsListViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)

        cls.nuts_subclass = ClassStructFactory(
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )

        cls.int_param_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.int_enum_type = ClassStruct.objects.get(pk=EnumsIds.INT)

        cls.par1 = ParametrFactory(
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei,
        )
        cls.par2 = ParametrFactory(
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei,
        )
        cls.par3 = ParametrFactory(
            parametr_type=cls.int_enum_type,
            par_ei=cls.base_ei,
        )

        cls.parclass1 = ParClassFactory(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            min_value=1,
            max_value=10,
            num=1,
        )
        cls.parclass2 = ParClassFactory(
            class_field=cls.nuts_subclass,
            parametr=cls.par2,
            min_value=1,
            max_value=10,
            num=2,
        )
        cls.parclass3 = ParClassFactory(
            class_field=cls.nuts_subclass,
            parametr=cls.par3,
            min_value=None,
            max_value=None,
            num=3,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:params_list", args=[cls.nuts_subclass.pk])

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

    def test_uses_params_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/params.html")

    def test_has_params_in_context(self):
        self.client.force_login(self.allowed_user)        
        response = self.client.get(self.url)
        self.assertIn("params", response.context)

    def test_has_class_in_context(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("class", response.context)

    def test_corrrectly_renders_information(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        for parclass in (self.parclass1, self.parclass2):
            self.assertContains(response, parclass.parametr.name)
            self.assertContains(response, parclass.parametr.par_ei.short_name)
            if parclass.parametr.parametr_type.pk in NUMERIC_PARAMS:
                self.assertContains(response, parclass.min_value)
                self.assertContains(response, parclass.max_value)


class OperationClassCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.welding = ClassStruct.objects.get(pk=OperationConsts.WELDING)

        cls.valid_data = ClassFormData(
            main_class=cls.welding.pk,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:add_operation_class")
        cls.redirect_url = reverse("classes:index")

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

    def test_uses_operation_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/operation_class.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, self.valid_data)
        operation = ClassStruct.objects.last()
        self.assertEqual(operation.name, self.valid_data["name"])
        self.assertEqual(operation.short_name, self.valid_data["short_name"])
        self.assertEqual(operation.main_class.pk, self.valid_data["main_class"])

    def test_redirects_after_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.redirect_url)


class EconomicSubjectActivityCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.economic_activity_subject = ClassStruct.objects.get(
            pk=MetaConsts.ECONOMIC_ACTIVITY_SUBJECT
        )

        cls.valid_data = ClassFormData(
            main_class=cls.economic_activity_subject.pk,
        )

        cls.url = reverse("classes:add_eas_class")
        cls.redirect_url = reverse("classes:index")

    def test_uses_operation_class_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/eas_class.html")

    def test_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url, self.valid_data)
        subject = ClassStruct.objects.last()
        self.assertEqual(subject.name, self.valid_data["name"])
        self.assertEqual(subject.short_name, self.valid_data["short_name"])
        self.assertEqual(subject.main_class.pk, self.valid_data["main_class"])

    def test_redirects_after_a_POST_request(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.redirect_url)


class MeansOfLaborCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_main_class = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.valid_data = ClassFormData(
            main_class=cls.valid_main_class.pk,
        )

        cls.url = reverse("classes:add_mol_class")
        cls.redirect_url = reverse("classes:index")

    def test_uses_mol_class_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/mol_class.html")

    def test_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.post(self.url, self.valid_data)
        mol = ClassStruct.objects.last()
        self.assertEqual(mol.name, self.valid_data["name"])
        self.assertEqual(mol.short_name, self.valid_data["short_name"])
        self.assertEqual(mol.main_class.pk, self.valid_data["main_class"])

    def test_redirects_after_a_POST_request(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.redirect_url)


class QualificationClassCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.qualification = ClassStruct.objects.get(pk=MetaConsts.QUALIFICATION)

        cls.valid_data = ClassFormData(
            main_class=cls.qualification.pk,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:add_qualification_class")
        cls.redirect_url = reverse("classes:index")

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

    def test_uses_qualification_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/qualification_class.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, self.valid_data)
        qualification = ClassStruct.objects.last()
        self.assertEqual(qualification.name, self.valid_data["name"])
        self.assertEqual(qualification.short_name, self.valid_data["short_name"])
        self.assertEqual(qualification.main_class.pk, self.valid_data["main_class"])

    def test_redirects_after_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.redirect_url)


class ProfessionClassCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.profession = ClassStruct.objects.get(pk=MetaConsts.PROFESSION)

        cls.valid_data = ClassFormData(
            main_class=cls.profession.pk,
        )

        cls.allowed_role = Role.objects.get(code=RoleCodes.HANDBOOK_EXECUTIVE)
        cls.not_allowed_role = Role.objects.get(code=RoleCodes.BUILDER)

        cls.allowed_user = UserFactory(role=cls.allowed_role)
        cls.not_allowed_user = UserFactory(role=cls.not_allowed_role)

        cls.url = reverse("classes:add_profession_class")
        cls.redirect_url = reverse("classes:index")

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

    def test_uses_profession_class_template(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/profession_class.html")

    def test_renders_form(self):
        self.client.force_login(self.allowed_user)
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        self.client.post(self.url, self.valid_data)
        profession = ClassStruct.objects.last()
        self.assertEqual(profession.name, self.valid_data["name"])
        self.assertEqual(profession.short_name, self.valid_data["short_name"])
        self.assertEqual(profession.main_class.pk, self.valid_data["main_class"])

    def test_redirects_after_a_POST_request(self):
        self.client.force_login(self.allowed_user)
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, self.redirect_url)
