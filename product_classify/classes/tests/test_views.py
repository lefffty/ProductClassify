from django.test import TestCase
from django.utils.html import escape
from django.urls import reverse

from http import HTTPStatus
from parameterized import parameterized
from faker import Faker
from unittest.mock import patch
from random import randint

from parametr.models import Parametr
from parametr.constants import ParametrConsts

from ei.models import Ei
from ei.constants import KILOGRAM_ID

from classes.models import ClassStruct, ParClass
from classes.forms import ProdClassForm, EnumClassForm
from classes.errors import ClassStructErrors, ParClassErrors
from classes.constants import (
    ProdClassConsts, EnumClassConsts, ProductsConsts, EnumsIds, ParamIds
)


class MainPageTemplateViewTest(TestCase):
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
        self.assertContains(response, '<nav id="menu">')


class CategoryClassesListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        nuts_class = ClassStruct.objects.get(pk=3)

        ClassStruct.objects.create(
            name="Nuts subclass",
            short_name="subclass",
            main_class=nuts_class,
            base_ei=None,
        )

    @parameterized.expand([
        (3,),
        (4,),
        (5,),
    ])
    def test_category_classes_view_returns_ok_status_code(self, class_id):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.expand([
        (3,),
        (4,),
        (5,),
    ])
    def test_category_classes_view_uses_category_template(self, class_id):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertTemplateUsed(response, "classes/category.html")

    @parameterized.expand([
        (3, 1),
        (4, 0),
        (5, 0),
    ])
    def test_category_classes_view_displays_correct_number_of_subclasses(self, class_id, expected_count):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": class_id}))
        self.assertEqual(len(response.context["classes"]), expected_count)

    def test_category_classes_view_returns_not_found_error_if_given_class_id_is_invalid(self):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 6}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        
    def test_fastener_classes_are_in_context(self):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 3}))
        self.assertIn("fastener_classes", response.context)

    def test_main_class_in_context(self):
        response = self.client.get(reverse("classes:category_classes", kwargs={"class_id": 3}))
        self.assertIn("main_class", response.context)


class ProdClassCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.fake = Faker()
        cls.url = reverse("classes:add_prod_class")
        cls.redirect_url = reverse("classes:index")

        cls.data = {
            "name": cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            "base_ei": "",
            "main_class": cls.nuts_class.pk,
        }
        cls.invalid_data = {
            "name": cls.fake.name(),
            "short_name": "",
            "base_ei": "",
            "main_class": "",
        }

    def test_prod_class_create_view_uses_prod_class_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_prod_class_create_view_renders_create_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_can_save_a_POST_request(self):
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=self.url,
            data=self.data
        )
        new_class = ClassStruct.objects.last()
        self.assertEqual(ClassStruct.objects.count(), count_before + 1)
        self.assertEqual(new_class.name, self.data["name"])
        self.assertEqual(new_class.short_name, self.data["short_name"])
        self.assertIsNone(new_class.base_ei)

    def test_redirects_after_POST(self):
        response = self.client.post(
            path=self.url,
            data=self.data
        )
        self.assertRedirects(response, self.redirect_url)

    def test_for_invalid_input_renders_prod_class_template(self):
        response = self.client.post(
            path=self.url,
            data=self.invalid_data,
        )
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_invalid_prod_class_data_is_not_saved(self):
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=self.url,
            data=self.invalid_data
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)

    def test_empty_main_class_validation_error_is_shown_on_page(self):
        response = self.client.post(
            path=self.url,
            data={
                "name": self.fake.name(),
                "short_name": "",
                "base_ei": "",
                "main_class": "",
            }
        )
        self.assertContains(response, escape(ClassStructErrors.EMPTY_MAIN_CLASS_ERROR))

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(
            path=self.url,
            data={
                "name": "",
                "short_name": "",
                "base_ei": "",
                "main_class": self.nuts_class.pk,
            }
        )
        self.assertContains(response, escape(ClassStructErrors.EMPTY_NAME_ERROR))


class EnumClassCreateViewTest(TestCase):    
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("classes:add_enum_class")
        cls.redirect_url = reverse("classes:index")
        cls.fake = Faker()
        cls.int_enum = ClassStruct.objects.get(pk=EnumsIds.INT)

        cls.valid_data = {
            "name": cls.fake.name()[:EnumClassConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:EnumClassConsts.SHORT_NAME_MAX_LENGTH],
            "base_ei": "",
            "main_class": cls.int_enum.pk,
        }
        cls.invalid_data = {
            "name": "",
            "short_name": "",
            "base_ei": "",
            "main_class": "",
        }

    def test_enum_class_create_view_uses_enum_class_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_enum_class_create_view_render_enum_class_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_enum_class_create_view_can_save_a_POST_request(self):
        count_before = ClassStruct.objects.count()
        response = self.client.post(
            path=self.url,
            data=self.valid_data
        )
        if response.status_code == HTTPStatus.OK:
            print(response.context["form"].errors)
        new_enum_class = ClassStruct.objects.last()
        self.assertEqual(ClassStruct.objects.count(), count_before + 1)
        self.assertEqual(new_enum_class.name, self.valid_data["name"])
        self.assertEqual(new_enum_class.short_name, self.valid_data["short_name"])
        self.assertEqual(new_enum_class.main_class.pk, self.valid_data["main_class"])
        self.assertIsNone(new_enum_class.base_ei)

    def test_enum_class_create_view_redirect_after_correct_POST_request(self):
        response = self.client.post(
            path=self.url,
            data=self.valid_data
        )
        self.assertRedirects(response, self.redirect_url)

    def test_enum_class_create_view_renders_enum_class_template_for_invalid_input(self):
        response = self.client.post(
            path=self.url,
            data=self.invalid_data
        )
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(
            path=self.url,
            data={
                "name": "",
                "short_name": "",
                "main_class": self.int_enum.pk,
                "base_ei": ""
            }
        )
        self.assertContains(response, escape(ClassStructErrors.EMPTY_NAME_ERROR))

    def test_empty_main_class_validation_error_is_shown_on_page(self):
        response = self.client.post(
            path=self.url,
            data={
                "name": self.fake.name(),
                "short_name": "",
                "main_class": "",
                "base_ei": ""
            }
        )
        self.assertContains(response, escape(ClassStructErrors.EMPTY_MAIN_CLASS_ERROR))


class ClassUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.int_enum_class = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.base_ei = Ei.objects.get(pk=KILOGRAM_ID)
        cls.fake = Faker()

        cls.enum_class = ClassStruct.objects.create(
            name=cls.fake.name()[:EnumClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:EnumClassConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.int_enum_class,
        )
        cls.support_enum_class = ClassStruct.objects.create(
            name=cls.fake.name()[:EnumClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:EnumClassConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.enum_class,
        )
        cls.enum_class_edit_data = {
            "name": cls.fake.name()[:EnumClassConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:EnumClassConsts.SHORT_NAME_MAX_LENGTH],
            "base_ei": "",
            "main_class": cls.int_enum_class.pk,
        }
        cls.invalid_enum_class_edit_data = {
            "name": cls.fake.name()[:EnumClassConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:EnumClassConsts.SHORT_NAME_MAX_LENGTH],
            "base_ei": "",
            "main_class": cls.enum_class.pk,
        }
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.support_prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.prod_class,
        )
        cls.prod_class_edit_data = {
            "name": cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            "base_ei": cls.base_ei.pk,
            "main_class": cls.nuts_class.pk,
        }
        cls.invalid_prod_class_edit_data = {
            "name": cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            "base_ei": cls.base_ei.pk,
            "main_class": cls.prod_class.pk,
        }

    def test_class_update_view_uses_enum_class_template_for_enum_class(self):
        response = self.client.get(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
        )
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_class_update_view_uses_prod_class_template_for_prod_class(self):
        response = self.client.get(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
        )
        self.assertTemplateUsed(response, "classes/prod_class.html")

    def test_class_update_view_renders_enum_class_form_for_enum_class(self):
        response = self.client.get(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
        )
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], EnumClassForm)

    def test_class_update_view_renders_prod_class_form_for_prod_class(self):
        response = self.client.get(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
        )
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], ProdClassForm)

    def test_class_update_view_can_save_a_POST_request_for_prod_class(self):
        count_before = ClassStruct.objects.count()
        self.client.post(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
            data=self.prod_class_edit_data
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)
        updated_instance = ClassStruct.objects.get(pk=self.prod_class.pk)
        self.assertEqual(updated_instance.name, self.prod_class_edit_data["name"])
        self.assertEqual(updated_instance.short_name, self.prod_class_edit_data["short_name"])
        self.assertEqual(updated_instance.main_class.pk, self.prod_class_edit_data["main_class"])
        self.assertEqual(updated_instance.base_ei.pk, self.prod_class_edit_data["base_ei"])

    def test_class_update_view_can_save_a_POST_request_for_enum_class(self):
        count_before = ClassStruct.objects.count()
        response = self.client.post(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
            data=self.enum_class_edit_data
        )
        self.assertEqual(ClassStruct.objects.count(), count_before)
        updated_instance = ClassStruct.objects.get(pk=self.enum_class.pk)
        self.assertEqual(updated_instance.name, self.enum_class_edit_data["name"])
        self.assertEqual(updated_instance.short_name, self.enum_class_edit_data["short_name"])
        self.assertEqual(updated_instance.main_class.pk, self.enum_class_edit_data["main_class"])

    def test_class_update_view_redirects_after_correct_POST_request_for_prod_class(self):
        response = self.client.post(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
            data=self.prod_class_edit_data
        )
        redirect_url = reverse("classes:category_classes", args=[self.prod_class.main_class.pk])
        self.assertRedirects(response, redirect_url)

    def test_class_update_view_redirects_after_correct_POST_request_for_enum_class(self):
        response = self.client.post(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
            data=self.enum_class_edit_data
        )
        redirect_url = reverse("classes:category_classes", args=[self.enum_class.main_class.pk])
        self.assertRedirects(response, redirect_url)

    def test_detected_classificator_cycle_validation_error_is_shown_on_page_for_prod_class(self):
        response = self.client.post(
            path=reverse("classes:edit", args=[self.prod_class.pk]),
            data=self.invalid_prod_class_edit_data
        )
        self.assertContains(response, escape(ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR))

    def test_detected_classificator_cycle_validation_error_is_shown_on_page_for_enum_class(self):
        response = self.client.post(
            path=reverse("classes:edit", args=[self.enum_class.pk]),
            data=self.invalid_enum_class_edit_data
        )
        self.assertContains(response, escape(ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR))


class DeleteClassViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )
        cls.class_id = cls.nuts_subclass.pk
        cls.url = reverse("classes:delete", args=[cls.class_id])
        cls.redirect_url = reverse("classes:category_classes", args=[cls.nuts_class.pk])

    def test_delete_class_view_uses_enum_class_template(self):
        response = self.client.get(path=self.url)
        self.assertTemplateUsed(response, "classes/enum_class.html")

    def test_fastener_classes_are_in_context(self):
        response = self.client.get(path=self.url)
        self.assertIn("fastener_classes", response.context)

    def test_instance_is_in_context(self):
        response = self.client.get(path=self.url)
        self.assertIn("instance", response.context)

    def test_delete_class_view_correctly_deletes_given_class(self):
        self.client.post(path=self.url)
        self.assertEqual(ClassStruct.objects.filter(pk=self.nuts_subclass.pk).count(), 0)

    def test_delete_class_view_redirects_after_a_POST_request(self):
        response = self.client.post(path=self.url)
        self.assertRedirects(response, self.redirect_url, fetch_redirect_response=False)

    def test_delete_class_and_descendants_was_called_with_correct_arguments(self):
        with patch.object(
            ClassStruct,
            "delete_class_and_descendants"
        ) as mock_delete_class_and_descendants:
            self.client.post(path=self.url)
            mock_delete_class_and_descendants.assert_called_once()
            mock_delete_class_and_descendants.assert_called_with(self.class_id)


class ClassParamCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.int_param_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.int_enum_type = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)

        cls.par1 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei
        )
        cls.par2 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_enum_type,
            par_ei=cls.base_ei
        )
        cls.par3 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.agregat_type,
            par_ei=None
        )

        cls.valid_enum_type_data = {
            "class_field": cls.nuts_subclass.pk,
            "parametr": cls.par2.pk,
            "min_value": "",
            "max_value": "",
        }
        cls.valid_numeric_type_data = {
            "class_field": cls.nuts_subclass.pk,
            "parametr": cls.par1.pk,
            "min_value": randint(1, 100),
            "max_value": randint(101, 1000),            
        }
        cls.empty_class_field_data = {
            "class_field": "",
            "parametr": cls.par2.pk,
            "min_value": "",
            "max_value": "",
        }
        cls.empty_parametr_field_data = {
            "class_field": cls.nuts_subclass.pk,
            "parametr": "",
            "min_value": "",
            "max_value": "",
        }
        cls.agregat_type_data = {
            "class_field": cls.nuts_subclass.pk,
            "parametr": cls.par3.pk,
            "min_value": "",
            "max_value": "",
        }
        cls.mn_or_mx_specified_data = {
            "class_field": cls.nuts_subclass.pk,
            "parametr": cls.par2.pk,
            "min_value": randint(1, 100),
            "max_value": "",
        }
        cls.mn_gt_mx_data = {
            "class_field": cls.nuts_subclass.pk,
            "parametr": cls.par1.pk,
            "min_value": randint(101, 1000),
            "max_value": randint(1, 100),
        }

        cls.url = reverse("classes:add_param", args=[cls.nuts_subclass.pk])
        cls.redirect_url = reverse("classes:params_list", args=[cls.nuts_subclass.pk])

    def test_class_param_create_view_test_uses_par_class_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/param_class.html")

    def test_class_param_create_view_test_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_class_param_create_view_test_has_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_class_param_create_view_can_save_a_POST_enum_request(self):
        self.client.post(self.url, data=self.valid_enum_type_data)
        pair = ParClass.objects.first()
        self.assertEqual(pair.class_field.pk, self.valid_enum_type_data["class_field"])
        self.assertEqual(pair.parametr.pk, self.valid_enum_type_data["parametr"])
        self.assertIsNone(pair.min_value)
        self.assertIsNone(pair.max_value)

    def test_class_param_create_view_correctly_calculates_num_field(self):
        self.client.post(self.url, data=self.valid_numeric_type_data)
        self.client.post(self.url, data=self.valid_enum_type_data)
        p1 = ParClass.objects.first()
        p2 = ParClass.objects.last()
        self.assertEqual(p1.class_field, p2.class_field)
        self.assertEqual(p1.num, 1)
        self.assertEqual(p2.num, 2)

    def test_class_param_create_view_can_save_a_POST_numeric_request(self):
        self.client.post(self.url, data=self.valid_numeric_type_data)
        pair = ParClass.objects.first()
        self.assertEqual(pair.class_field.pk, self.valid_numeric_type_data["class_field"])
        self.assertEqual(pair.parametr.pk, self.valid_numeric_type_data["parametr"])
        self.assertEqual(pair.min_value, self.valid_numeric_type_data["min_value"])
        self.assertEqual(pair.max_value, self.valid_numeric_type_data["max_value"])

    def test_class_param_create_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.valid_numeric_type_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_class_field_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_class_field_data)
        self.assertContains(response, escape(ParClassErrors.EMPTY_CLASS_FIELD))

    def test_empty_parametr_field_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, self.empty_parametr_field_data)
        self.assertContains(response, escape(ParClassErrors.EMPTY_PAR_FIELD))

    def test_min_value_or_max_value_was_specified_for_enum_parametr_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.mn_or_mx_specified_data)
        self.assertContains(
            response,
            escape(ParClassErrors.ENUM_AGGREGATE_RANGE_ERROR.format(self.par2.name))
        )

    def test_min_value_is_gt_max_value_for_numeric_param_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.mn_gt_mx_data)
        self.assertContains(response, escape(ParClassErrors.MIN_GE_MAX))


class ClassParamUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.int_param_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.par1 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_param_type,
            par_ei=cls.base_ei
        )

        cls.parclass1 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            min_value=randint(1, 10),
            max_value=randint(11, 20),
            num=1
        )

        cls.valid_data = {
            "class_field": cls.nuts_subclass.pk,
            "parametr": cls.par1.pk,
            "min_value": randint(10, 20),
            "max_value": randint(21, 30)
        }

        cls.url = reverse("classes:edit_param", args=[cls.nuts_subclass.pk, cls.par1.pk])
        cls.redirect_url = reverse("classes:params_list", args=[cls.nuts_subclass.pk])

    def test_class_param_update_view_uses_param_class_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "classes/param_class.html")

    def test_class_param_update_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_class_param_update_view_can_save_a_POST_request(self):
        self.client.post(self.url, data=self.valid_data)
        p1 = ParClass.objects.first()
        self.assertEqual(p1.class_field.pk, self.valid_data["class_field"])
        self.assertEqual(p1.parametr.pk, self.valid_data["parametr"])
        self.assertTrue(p1.min_value, self.valid_data["min_value"])
        self.assertTrue(p1.max_value, self.valid_data["max_value"])

    def test_class_param_update_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.redirect_url)
