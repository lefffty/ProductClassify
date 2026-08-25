from tests.unit.base import BaseUnitTestCase
from django.urls import reverse
from django.utils.html import escape
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker
from PIL import Image
from io import BytesIO

from classes.models import ClassStruct, ParClass
from classes.constants import ProductsConsts, ClassStructConsts, ParamIds, EnumsIds, ProdClassConsts

from parametr.models import Parametr
from parametr.constants import ParametrConsts

from enums.models import Enums

from ei.models import Ei

from specifications.models import ProdComponent

from products.constants import ProdConsts
from products.models import Prod, ParProd
from products.errors import ProdErrors, CommonParProdErrors, EnumsParErrors, IntParErrors, DoubleParErrors


class ProductDetailViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.ei
        )
        cls.int_params = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )
        cls.parametr = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_params,
            par_ei=cls.ei
        )
        cls.parclass = ParClass.objects.create(
            class_field=cls.prod_class,
            parametr=cls.parametr,
            num=1,
            min_value=10,
            max_value=20,
        )

        cls.prod = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.prod_class,
            image=None,
        )
        cls.parprod = ParProd.objects.create(
            prod=cls.prod,
            par=cls.parametr,
            int_value=15,
            double_value=None,
            enum_val=None,
        )

        cls.url = reverse("products:detail", args=[cls.prod.pk])

    def test_product_detail_view_uses_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/detail.html")

    def test_product_detail_view_has_params_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("params", response.context)

    def test_product_detail_view_has_product_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("product", response.context)

    def test_product_detail_view_renders_correct_information_about_product(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.prod.pk)
        self.assertContains(response, self.prod.name)
        self.assertContains(response, self.prod.class_field.name)

    def test_product_detail_view_renders_correct_information_about_params(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.parametr.name)
        self.assertContains(response, self.parprod.value)


class ProductCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.FASTENER_ID)
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )

        name = cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH]
        short_name = cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]

        cls.data = {
            "name": name,
            "short_name": short_name,
            "class_field": cls.prod_class.pk,
            "image": "",
        }
        cls.empty_class_field_data = {
            "name": name,
            "short_name": short_name,
            "class_field": "",
            "image": ""
        }
        cls.empty_name_field_data = {
            "name": "",
            "short_name": short_name,
            "class_field": cls.prod_class.pk,
            "image": ""
        }

        cls.url = reverse("products:add")
        cls.redirect_url = reverse("classes:index")

    def test_product_create_view_uses_product_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/product.html")

    def test_product_create_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_product_create_view_can_save_a_POST_request(self):
        self.client.post(self.url, data=self.data)
        prod = Prod.objects.last()
        self.assertEqual(self.data["name"], prod.name)
        self.assertEqual(self.data["short_name"], prod.short_name)
        self.assertEqual(self.data["class_field"], prod.class_field.pk)
        self.assertEqual(self.data["image"], prod.image)

    def test_product_create_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_class_field_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_class_field_data)
        self.assertContains(response, ProdErrors.EMPTY_CLASS_FIELD)

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_name_field_data)
        self.assertContains(response, ProdErrors.EMPTY_NAME_FIELD)


class ProductUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.prod_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=cls.nuts_class
        )

        old_name = cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH]
        old_short_name = cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]

        cls.prod = Prod.objects.create(
            name=old_name,
            short_name=old_short_name,
            class_field=cls.prod_class,
            image=None,
        )

        new_name = cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH]
        new_short_name = cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]

        cls.data = {
            "name": new_name,
            "short_name": new_short_name,
            "class_field": cls.prod_class.pk,
            "image": cls._create_test_image(),
        }
        cls.empty_class_field_data = {
            "name": new_name,
            "short_name": new_short_name,
            "class_field": "",
            "image": ""
        }
        cls.empty_name_field_data = {
            "name": "",
            "short_name": new_short_name,
            "class_field": cls.prod_class.pk,
            "image": ""
        }

        cls.url = reverse("products:edit", args=[cls.prod.pk])
        cls.redirect_url = reverse("products:detail", args=[cls.prod.pk])

    def _create_test_image(extension='jpg'):
        image = Image.new('RGB', (100, 100), color='red')
        file = BytesIO()
        format = 'JPEG' if extension == 'jpg' else 'PNG'
        image.save(file, format=format)
        file.seek(0)
        return SimpleUploadedFile(
            f"test.{extension}",
            file.read(),
            content_type=f"image/{extension if extension != 'jpg' else 'jpeg'}"
        )

    def test_product_update_view_uses_product_html(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/product.html")

    def test_product_update_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_product_update_view_has_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_product_update_view_can_save_a_POST_request(self):
        self.client.post(self.url, data=self.data)
        prod = Prod.objects.last()
        self.assertEqual(self.data["name"], prod.name)
        self.assertEqual(self.data["short_name"], prod.short_name)
        self.assertEqual(self.data["class_field"], prod.class_field.pk)
        self.assertIsNotNone(prod.image)

    def test_product_update_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_class_field_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_class_field_data)
        self.assertContains(response, ProdErrors.EMPTY_CLASS_FIELD)

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_name_field_data)
        self.assertContains(response, ProdErrors.EMPTY_NAME_FIELD)


class ProductDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.instance = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_class,
        )

        cls.url = reverse("products:delete", args=[cls.instance.pk])
        cls.redirect_url = reverse("products:class_products", kwargs={
            "main_class_id": cls.nuts_class.main_class.pk,
            "class_id": cls.nuts_class.pk,
        })

    def test_product_delete_view_uses_product_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/product.html")

    def test_product_delete_view_can_save_a_POST_request(self):
        count_before = Prod.objects.count()
        self.client.post(self.url)
        self.assertEqual(Prod.objects.count(), count_before - 1)

    def test_product_delete_view_redirects_after_POST_request(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class ProductParamCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.int_type_par = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.double_type_par = ClassStruct.objects.get(pk=ParamIds.DOUBLE)
        cls.int_enum_par = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.int_enum_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.int_enum_par
        )
        cls.product = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=None
        )
        cls.par1 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_enum_par,
            par_ei=cls.base_ei,
        )
        cls.par2 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_type_par,
            par_ei=cls.base_ei,
        )
        cls.par3 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_type_par,
            par_ei=cls.base_ei
        )
        cls.par4 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.double_type_par,
            par_ei=cls.base_ei
        )
        cls.enum1 = Enums.objects.create(
            enum=cls.int_enum_class,
            num=1,
            name=None,
            short_name=None,
            int_value=5,
            double_value=None,
            image=None
        )
        cls.parclass1 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            min_value=None,
            max_value=None,
            num=1
        )
        cls.parclass2 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par2,
            min_value=1,
            max_value=10,
            num=2
        )
        cls.parclass3 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par4,
            min_value=1,
            max_value=10,
            num=2
        )

        cls.valid_enum_data = {
            "par": cls.par1.pk,
            "prod": cls.product.pk,
            "int_value": "",
            "double_value": "",
            "enum_val": cls.enum1.pk,
        }
        cls.valid_numeric_data = {
            "par": cls.par2.pk,
            "prod": cls.product.pk,
            "int_value": 5,
            "double_value": "",
            "enum_val": "",
        }

        # общие ошибки
        cls.empty_parametr_data = {
            "par": "",
            "prod": cls.product.pk,
            "int_value": 5,
            "double_value": "",
            "enum_val": "",
        }
        cls.empty_prod_data = {
            "par": cls.par2.pk,
            "prod": "",
            "int_value": 5,
            "double_value": "",
            "enum_val": "",
        }
        cls.invalid_par_data = {
            "par": cls.par3.pk,
            "prod": cls.product.pk,
            "int_value": 5,
            "double_value": "",
            "enum_val": "",
        }

        # данные форм для обработки ошибок валидации параметров-перечислений
        cls.int_value_specified_data = {
            "par": cls.par1.pk,
            "prod": cls.product.pk,
            "int_value": 1,
            "double_value": "",
            "enum_val": cls.enum1.pk,
        }
        cls.double_value_specified_data = {
            "par": cls.par1.pk,
            "prod": cls.product.pk,
            "int_value": "",
            "double_value": 1.0,
            "enum_val": cls.enum1.pk,
        }
        cls.empty_enum_val_data = {
            "par": cls.par1.pk,
            "prod": cls.product.pk,
            "int_value": "",
            "double_value": "",
            "enum_val": "",
        }

        # данные форм для обработки ошибок валидации целочисленных параметров
        cls.double_val_specified_int_data = {
            "par": cls.par2.pk,
            "prod": cls.product.pk,
            "int_value": 5,
            "double_value": 3,
            "enum_val": "",
        }
        cls.enum_val_specified_int_data = {
            "par": cls.par2.pk,
            "prod": cls.product.pk,
            "int_value": 5,
            "double_value": "",
            "enum_val": cls.enum1.pk,
        }
        cls.empty_int_field_int_data = {
            "par": cls.par2.pk,
            "prod": cls.product.pk,
            "int_value": "",
            "double_value": "",
            "enum_val": "",
        }
        cls.int_field_not_in_range_int_data = {
            "par": cls.par2.pk,
            "prod": cls.product.pk,
            "int_value": 100,
            "double_value": "",
            "enum_val": "",
        }

        # данные форм для обработки ошибок валидации вещественных параметров
        cls.int_val_specified_double_data = {
            "par": cls.par4.pk,
            "prod": cls.product.pk,
            "int_value": 100,
            "double_value": "",
            "enum_val": "",
        }
        cls.enum_val_specified_double_data = {
            "par": cls.par4.pk,
            "prod": cls.product.pk,
            "int_value": "",
            "double_value": "",
            "enum_val": cls.enum1.pk,
        }
        cls.empty_double_field_double_data = {
            "par": cls.par4.pk,
            "prod": cls.product.pk,
            "int_value": "",
            "double_value": "",
            "enum_val": "",
        }
        cls.double_field_not_in_range_double_data = {
            "par": cls.par4.pk,
            "prod": cls.product.pk,
            "int_value": "",
            "double_value": 100,
            "enum_val": "",
        }

        cls.url = reverse("products:add_param", args=[cls.product.pk])
        cls.redirect_url = reverse("products:detail", args=[cls.product.pk])

    def test_product_param_create_view_uses_prodparam_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/prodparam.html")

    def test_product_param_create_view_has_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_product_param_create_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_product_param_create_view_can_save_a_POST_request_for_enum_parametr(self):
        self.client.post(self.url, data=self.valid_enum_data)
        self.assertEqual(ParProd.objects.count(), 1)
        first = ParProd.objects.first()
        self.assertEqual(first.par.pk, self.valid_enum_data["par"])
        self.assertEqual(first.prod.pk, self.valid_enum_data["prod"])
        self.assertEqual(first.enum_val.pk, self.valid_enum_data["enum_val"])
        self.assertIsNone(first.int_value)
        self.assertIsNone(first.double_value)

    def test_product_param_create_view_can_save_a_POST_request_for_numeric_parametr(self):
        self.client.post(self.url, data=self.valid_numeric_data)
        self.assertEqual(ParProd.objects.count(), 1)
        first = ParProd.objects.first()
        self.assertEqual(first.par.pk, self.valid_numeric_data["par"])
        self.assertEqual(first.prod.pk, self.valid_numeric_data["prod"])
        self.assertEqual(first.int_value, self.valid_numeric_data["int_value"])
        self.assertIsNone(first.enum_val)
        self.assertIsNone(first.double_value)

    def test_product_param_create_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.valid_numeric_data)
        self.assertRedirects(response, self.redirect_url)

    def test_empty_parametr_field_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_parametr_data)
        self.assertContains(response, CommonParProdErrors.EMPTY_PAR_FIELD)

    def test_empty_prod_field_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.empty_prod_data)
        self.assertContains(response, CommonParProdErrors.EMPTY_PROD_FIELD)

    def test_parametr_not_in_class_params_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.invalid_par_data)
        self.assertContains(response, escape(CommonParProdErrors.INVALID_PAR.format(self.par3.name, self.nuts_subclass.name)))

    def test_int_value_specified_validation_error_is_shown_on_page_for_enum_parametr(self):
        response = self.client.post(self.url, data=self.int_value_specified_data)
        self.assertContains(response, EnumsParErrors.INT_FIELD_SPECIFIED)

    def test_double_value_specified_validation_error_is_shown_on_page_for_enum_parametr(self):
        response = self.client.post(self.url, data=self.double_value_specified_data)
        self.assertContains(response, EnumsParErrors.DOUBLE_FIELD_SPECIFIED)

    def test_empty_enum_val_validation_error_is_shown_on_page_for_enum_parametr(self):
        response = self.client.post(self.url, data=self.empty_enum_val_data)
        self.assertContains(response, EnumsParErrors.ENUM_FIELD_EMPTY)

    def test_double_value_specified_validation_error_is_shown_on_page_for_int_type_par(self):
        response = self.client.post(self.url, data=self.double_val_specified_int_data)
        self.assertContains(response, IntParErrors.DOUBLE_FIELD_SPECIFIED)

    def test_enum_val_specified_validation_error_is_shown_on_page_for_int_type_par(self):
        response = self.client.post(self.url, data=self.enum_val_specified_int_data)
        self.assertContains(response, IntParErrors.ENUM_FIELD_SPECIFIED)

    def test_empty_int_value_validation_error_is_shown_on_page_for_int_type_par(self):
        response = self.client.post(self.url, data=self.empty_int_field_int_data)
        self.assertContains(response, IntParErrors.INT_FIELD_EMPTY)

    def test_int_value_not_in_range_validation_error_is_shown_on_page_for_int_type_par(self):
        response = self.client.post(self.url, data=self.int_field_not_in_range_int_data)
        self.assertIn(
            IntParErrors.INVALID_RANGE.format(
                int(self.parclass2.min_value),
                int(self.parclass2.max_value)
            ),
            response.context["form"].non_field_errors()
        )

    def test_int_value_specified_validation_error_is_shown_on_page_for_double_type_par(self):
        response = self.client.post(self.url, data=self.int_val_specified_double_data)
        self.assertContains(response, DoubleParErrors.INT_FIELD_SPECIFIED)

    def test_enum_val_specified_validation_error_is_shown_on_page_for_double_type_par(self):
        response = self.client.post(self.url, data=self.enum_val_specified_double_data)
        self.assertContains(response, DoubleParErrors.ENUM_FIELD_SPECIFIED)

    def test_empty_double_value_validation_error_is_shown_on_page_for_double_type_par(self):
        response = self.client.post(self.url, data=self.empty_double_field_double_data)
        self.assertContains(response, DoubleParErrors.DOUBLE_FIELD_EMPTY)

    def test_double_value_not_in_range_validation_error_is_shown_on_page_for_double_type_par(self):
        response = self.client.post(self.url, data=self.double_field_not_in_range_double_data)
        self.assertIn(
            DoubleParErrors.INVALID_RANGE.format(
                self.parclass3.min_value,
                self.parclass3.max_value
            ),
            response.context["form"].non_field_errors()
        )


class ProductParamDeleteViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.int_enum_par = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.int_enum_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.int_enum_par
        )
        cls.product = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=None
        )
        cls.par1 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_enum_par,
            par_ei=cls.base_ei,
        )
        cls.enum1 = Enums.objects.create(
            enum=cls.int_enum_class,
            num=1,
            name=None,
            short_name=None,
            int_value=5,
            double_value=None,
            image=None
        )
        cls.parprod = ParProd.objects.create(
            prod=cls.product,
            par=cls.par1,
            int_value=None,
            double_value=None,
            enum_val=cls.enum1  
        )

        cls.url = reverse("products:delete_param", args=[cls.product.pk, cls.par1.pk])
        cls.redirect_url = reverse("products:detail", args=[cls.product.pk])

    def test_product_param_delete_view_uses_prodparam_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/prodparam.html")

    def test_product_param_delete_view_has_instance_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("instance", response.context)

    def test_product_param_delete_view_can_save_a_POST_request(self):
        self.assertEqual(ParProd.objects.count(), 1)
        self.client.post(self.url)
        self.assertEqual(ParProd.objects.count(), 0)

    def test_product_param_delete_view_redirects_after_POST_request(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.redirect_url)


class ProductParamUpdateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.base_ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.int_enum_par = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.int_type_par = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.nuts_class,
        )
        cls.int_enum_class = ClassStruct.objects.create(
            name=cls.fake.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=cls.base_ei,
            main_class=cls.int_enum_par
        )
        cls.product = Prod.objects.create(
            name=cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=None
        )
        cls.par1 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_enum_par,
            par_ei=cls.base_ei,
        )
        cls.par2 = Parametr.objects.create(
            name=cls.fake.name()[:ParametrConsts.NAME_MAX_LENGTH],
            short_name=cls.fake.name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH],
            parametr_type=cls.int_type_par,
            par_ei=cls.base_ei,
        )
        cls.enum1 = Enums.objects.create(
            enum=cls.int_enum_class,
            num=1,
            name=None,
            short_name=None,
            int_value=5,
            double_value=None,
            image=None
        )
        cls.enum2 = Enums.objects.create(
            enum=cls.int_enum_class,
            num=2,
            name=None,
            short_name=None,
            int_value=10,
            double_value=None,
            image=None
        )
        cls.parclass1 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            min_value=None,
            max_value=None,
            num=1
        )
        cls.parclass2 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par2,
            min_value=1,
            max_value=100,
            num=1
        )
        cls.parprod1 = ParProd.objects.create(
            prod=cls.product,
            par=cls.par1,
            int_value=None,
            double_value=None,
            enum_val=cls.enum1  
        )
        cls.parprod2 = ParProd.objects.create(
            prod=cls.product,
            par=cls.par2,
            int_value=50,
            double_value=None,
            enum_val=None,
        )

        cls.enum_update_data = {
            "par": cls.par1.pk,
            "prod": cls.product.pk,
            "int_value": "",
            "double_value": "",
            "enum_val": cls.enum2.pk,
        }
        cls.numeric_update_data = {
            "par": cls.par2.pk,
            "prod": cls.product.pk,
            "int_value": 50,
            "double_value": "",
            "enum_val": "",
        }

        cls.url1 = reverse("products:edit_param", args=[cls.product.pk, cls.par1.pk])
        cls.url2 = reverse("products:edit_param", args=[cls.product.pk, cls.par2.pk])
        cls.redirect_url = reverse("products:detail", args=[cls.product.pk])

    def test_product_param_update_view_uses_prodparam_template(self):
        response = self.client.get(self.url1)
        self.assertTemplateUsed(response, "products/prodparam.html")

    def test_product_param_update_view_renders_form(self):
        response = self.client.get(self.url1)
        self.assertIn("form", response.context)

    def test_product_param_update_view_has_instance_in_context(self):
        response = self.client.get(self.url1)
        self.assertIn("instance", response.context)

    def test_product_param_update_view_can_save_a_POST_request_for_enum_parametr(self):
        self.client.post(self.url1, data=self.enum_update_data)
        instance = ParProd.objects.first()
        self.assertEqual(instance.par.pk, self.enum_update_data["par"])
        self.assertEqual(instance.prod.pk, self.enum_update_data["prod"])
        self.assertEqual(instance.enum_val.pk, self.enum_update_data["enum_val"])
        self.assertIsNone(instance.int_value)
        self.assertIsNone(instance.double_value)

    def test_product_param_update_view_can_save_a_POST_request_for_numeric_parametr(self):
        self.client.post(self.url2, data=self.numeric_update_data)
        instance = ParProd.objects.last()
        self.assertEqual(instance.par.pk, self.numeric_update_data["par"])
        self.assertEqual(instance.prod.pk, self.numeric_update_data["prod"])
        self.assertEqual(instance.int_value, self.numeric_update_data["int_value"])
        self.assertIsNone(instance.enum_val)
        self.assertIsNone(instance.double_value)

    def test_product_param_update_view_redirects_after_POST_request(self):
        response = self.client.post(self.url1, data=self.enum_update_data)
        self.assertRedirects(response, self.redirect_url)


class ModificationCreateViewTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        fake = Faker()

        nuts_name = fake.name()[:ClassStructConsts.NAME_MAX_LENGTH]
        nuts_short_name = fake.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH]
        cls.ei = Ei.objects.first()
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=nuts_name,
            short_name=nuts_short_name,
            main_class=cls.nuts_class,
            base_ei=cls.ei,
        )
        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod_name = fake.name()[:ProdConsts.NAME_MAX_LENGTH]
        prod_short_name = fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]
        cls.prod = Prod.objects.create(
            name=prod_name,
            short_name=prod_short_name,
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=800,
            ei=cls.ei,
            modification=None
        )
        cls.component_prod = Prod.objects.create(
            name=fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            short_name=fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH],
            class_field=cls.nuts_subclass,
            image=cls.image,
            cost=800,
            ei=cls.ei,
            modification=None
        )
        cls.prodcomponent = ProdComponent.objects.create(
            parent_prod=cls.prod,
            component=cls.component_prod,
            num=1,
            quantity=400,
        )

        mod_name = fake.name()[:ProdConsts.NAME_MAX_LENGTH]
        mod_short_name = fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]

        cls.valid_data = {
            "name": mod_name,
            "short_name": mod_short_name,
        }
        cls.invalid_data = {
            "name": "",
            "short_name": mod_short_name,
        }

        cls.url = reverse("products:create_modification", args=[cls.prod.pk])

    def test_create_modification_view_uses_modification_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/modification.html")

    def test_create_modification_view_has_fastener_classes_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("fastener_classes", response.context)

    def test_create_modification_view_renders_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_create_modification_view_can_save_a_POST_request(self):
        self.client.post(self.url, data=self.valid_data)
        prod = Prod.objects.last()
        self.assertEqual(prod.name, self.valid_data["name"])
        self.assertEqual(prod.short_name, self.valid_data["short_name"])
        self.assertEqual(prod.cost, self.prod.cost)
        self.assertEqual(prod.image, self.prod.image)
        self.assertEqual(prod.ei, self.prod.ei)
        self.assertEqual(prod.modification.pk, self.prod.pk)
        self.assertEqual(prod.class_field, self.prod.class_field)
        self.assertEqual(ProdComponent.objects.filter(parent_prod=prod.pk).count(), 1)

    def test_create_modification_view_redirects_after_POST_request(self):
        response = self.client.post(self.url, data=self.valid_data)
        modification = Prod.objects.last()
        redirect_url = reverse("products:detail", args=[modification.pk])
        self.assertRedirects(response, redirect_url)

    def test_empty_name_validation_error_is_shown_on_page(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertContains(response, ProdErrors.EMPTY_NAME_FIELD)
