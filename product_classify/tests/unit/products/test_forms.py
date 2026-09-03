from tests.unit.base import BaseUnitTestCase
from django.db.models import QuerySet
from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image
from decimal import Decimal
from io import BytesIO
from faker import Faker

from classes.models import ClassStruct, ParClass
from classes.constants import ProductsConsts, EnumsIds, ParamIds, ProdClassConsts
from parametr.models import Parametr
from ei.models import Ei
from enums.models import Enums

from products.constants import ProdConsts
from products.models import Prod, ParProd
from products.forms import ProdForm, ParProdForm, ModificationForm, SearchForm
from products.errors import IntParErrors, DoubleParErrors, ProdErrors


def create_image(extension: str = "jpg"):
    image = Image.new("RGB", (100, 100), "red")
    file = BytesIO()
    format = "JPEG" if extension == "jpg" else "PNG"
    image.save(file, format)
    file.seek(0)
    return SimpleUploadedFile(
        f"test.{extension}",
        file.read(),
        content_type=f"image/{extension if extension != 'jpg' else 'jpeg'}",
    )


class ProdFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.NUTS_CLASS = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.INVALID_CLASS = ClassStruct.objects.get(pk=EnumsIds.STRING)
        cls.EI = Ei.objects.first()

        cls.PNG_IMAGE = create_image("png")
        cls.JPG_IMAGE = create_image("jpg")
        cls.GIF_IMAGE = create_image("gif")

        cls.PROD_NAME = "Test product name"
        cls.PROD_SHORT_NAME = "Test sh. name"
        cls.NEW_PROD_NAME = "New test product name"
        cls.NEW_PROD_SHORT_NAME = "New sh. nm."

    def test_class_field_queryset_is_products_classes(self):
        """Проверяет, что поле class_field использует queryset с объектами ClassStruct.products()."""
        form = ProdForm()
        self.assertIsInstance(form.fields["class_field"].queryset, QuerySet)
        self.assertEqual(len(form.fields["class_field"].queryset), 5)

    def test_class_field_is_required(self):
        """Проверяет, что поле class_field обязательно для заполнения."""
        form_data = {
            "class_field": None,
            "name": self.PROD_NAME,
            "short_name": None,
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn(
            form.errors["class_field"][0],
            "Поле для родительского класса изделия необходимо заполнить",
        )

    def test_name_is_required(self):
        """Проверяет, что поле name обязательно для заполнения."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": None,
            "short_name": None,
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["name"][0], "Поле для названия класса необходимо заполнить"
        )

    def test_short_name_is_optional_accepts_empty_string(self):
        """Проверяет, что поле short_name может быть пустой строкой и форма проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": None,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_short_name_is_optional_accepts_none(self):
        """Проверяет, что поле short_name может быть равно None и форма проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": "",
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_cost_field_is_optional(self):
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
            "cost": Decimal("1.0"),
        }
        form = ProdForm(form_data)
        self.assertTrue(form.is_valid())

    def test_ei_field_is_optional(self):
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
            "ei": self.EI,
        }
        form = ProdForm(form_data)
        self.assertTrue(form.is_valid())

    def test_image_field_is_optional_accepts_none(self):
        """Проверяет, что поле image может быть равно None и форма проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_invalid_class_field_object_raises_validation_error(self):
        """Проверяет, что выбор class_field, не входящего в products(), вызывает ошибку валидации."""
        form_data = {
            "class_field": self.INVALID_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_non_jpg_or_png_image_raises_validation_error(self):
        """Проверяет, что загрузка изображения с недопустимым расширением (не jpg/png) вызывает ошибку валидации."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.GIF_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

    def test_jpg_image_is_valid(self):
        """Проверяет, что загрузка изображения .jpg проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.JPG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_png_image_is_valid(self):
        """Проверяет, что загрузка изображения .png проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_object_with_minimal_requirements_is_valid(self):
        """Проверяет, что форма с минимально необходимыми данными (class_field, name) проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": None,
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_object_with_minimal_requirements_is_saved_correctly(self):
        """Проверяет, что форма с минимальными данными корректно сохраняет объект."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": "",
        }
        form_files = {
            "image": None,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.class_field, form_data["class_field"])
        self.assertNotEqual(obj.image.name, form_files["image"])

    def test_object_with_maximum_requirements_is_valid(self):
        """Проверяет, что форма со всеми заполненными полями (включая short_name и image) проходит валидацию."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
            "cost": Decimal("1.0"),
            "ei": self.EI,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_object_with_maximum_requirements_is_saved_correctly(self):
        """Проверяет, что форма со всеми полями корректно сохраняет объект."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
            "ei": self.EI,
            "cost": Decimal("1.0"),
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.class_field, form_data["class_field"])
        self.assertEqual(obj.ei, form_data["ei"])
        self.assertEqual(obj.cost, form_data["cost"])
        self.assertNotEqual(obj.image.name, form_files["image"])

    def test_class_field_relationship(self):
        """Проверяет, что объект связывается с правильным class_field через обратную связь."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        obj = form.save()

        self.assertIn(obj, self.NUTS_CLASS.class_products.all())

    def test_ei_relationship(self):
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
            "ei": self.EI
        }
        form = ProdForm(form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()

        self.assertIn(obj, self.EI.prod_set.all())

    def test_negative_cost_field_value_raises_validation_error(self):
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
            "cost": Decimal("-1.0")
        }
        form = ProdForm(form_data)
        self.assertFalse(form.is_valid())

    def test_edit_existing_object_updates_fields(self):
        """Проверяет, что при редактировании существующего объекта все поля обновляются корректно."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        obj = form.save()

        new_form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.NEW_PROD_NAME,
            "short_name": self.NEW_PROD_SHORT_NAME,
        }
        new_form_files = {
            "image": self.JPG_IMAGE,
        }
        form = ProdForm(data=new_form_data, files=new_form_files, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, new_form_data["name"])
        self.assertEqual(obj.short_name, new_form_data["short_name"])
        self.assertEqual(obj.class_field, new_form_data["class_field"])
        self.assertNotEqual(obj.image.name, new_form_files["image"])

    def test_edit_without_image_keeps_old_image(self):
        """Проверяет, что при редактировании без загрузки нового изображения старый файл сохраняется."""
        form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.PROD_NAME,
            "short_name": self.PROD_SHORT_NAME,
        }
        form_files = {
            "image": self.PNG_IMAGE,
        }
        form = ProdForm(data=form_data, files=form_files)
        obj = form.save()

        new_form_data = {
            "class_field": self.NUTS_CLASS,
            "name": self.NEW_PROD_NAME,
            "short_name": self.NEW_PROD_SHORT_NAME,
        }
        form = ProdForm(data=new_form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, new_form_data["name"])
        self.assertEqual(obj.short_name, new_form_data["short_name"])
        self.assertEqual(obj.class_field, new_form_data["class_field"])
        self.assertNotEqual(obj.image.name, form_files["image"])


class ParProdFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.PARCLASS_INT_MIN_VALUE = 0.0
        cls.PARCLASS_INT_MAX_VALUE = 5.0
        cls.PARCLASS_DOUBLE_MIN_VALUE = 2.5
        cls.PARCLASS_DOUBLE_MAX_VALUE = 7.5
        cls.INT_VALUE = 3
        cls.DOUBLE_VALUE = 4.5

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_product_class = ClassStruct.objects.create(
            name="nuts_product_class",
            short_name="nuts_prod_class",
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.int_parametr_cls = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.double_parametr_cls = ClassStruct.objects.get(pk=ParamIds.DOUBLE)
        cls.int_enum_parametr_cls = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.int_enum = ClassStruct.objects.create(
            name="int_enum_class",
            short_name="int_enum",
            base_ei=None,
            main_class=cls.int_enum_parametr_cls,
        )

        cls.INT_PARAMETR = Parametr.objects.create(
            name="int_parametr",
            short_name="int_par",
            parametr_type=cls.int_parametr_cls,
        )
        cls.DOUBLE_PARAMETR = Parametr.objects.create(
            name="double_parametr",
            short_name="double_par",
            parametr_type=cls.double_parametr_cls,
        )
        cls.INVALID_INT_PARAMETR = Parametr.objects.create(
            name="parameter",
            short_name="param",
            parametr_type=cls.int_parametr_cls
        )
        cls.INT_ENUM_PARAMETR = Parametr.objects.create(
            name="parametr",
            short_name="par",
            parametr_type=cls.int_enum_parametr_cls
        )
        cls.ENUM_VAL = Enums.objects.create(
            enum=cls.int_enum,
            num=1,
            name="test_enum",
            short_name="test_enum",
            double_value=None,
            int_value=cls.INT_VALUE,
            image=None,
        )
        cls.PRODUCT = Prod.objects.create(
            name="nuts product",
            class_field=cls.nuts_product_class,
            short_name="",
        )

        cls.parclass1 = ParClass.objects.create(
            class_field=cls.nuts_product_class,
            parametr=cls.INT_PARAMETR,
            num=1,
            min_value=cls.PARCLASS_INT_MIN_VALUE,
            max_value=cls.PARCLASS_INT_MAX_VALUE,
        )
        cls.parclass2 = ParClass.objects.create(
            class_field=cls.nuts_product_class,
            parametr=cls.DOUBLE_PARAMETR,
            num=2,
            min_value=cls.PARCLASS_DOUBLE_MIN_VALUE,
            max_value=cls.PARCLASS_DOUBLE_MAX_VALUE
        )
        cls.parclass1 = ParClass.objects.create(
            class_field=cls.nuts_product_class,
            parametr=cls.INT_ENUM_PARAMETR,
            num=3,
            min_value=None,
            max_value=None,
        )

    def _create_par_prod_instance(self) -> ParProd:
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data)
        self.assertTrue(form.is_valid())

        instance = form.save()

        return instance

    def test_par_queryset_is_parameters(self,):
        form = ParProdForm()
        parameters_count = Parametr.parameters().count()
        self.assertIsInstance(form.fields["par"].queryset, QuerySet)
        self.assertEqual(form.fields["par"].queryset.count(), parameters_count)

    def test_prod_initial_is_not_none_if_prod_id_is_specified_in_constructor(self):
        form = ParProdForm(prod_id=self.PRODUCT.pk)
        self.assertIsNotNone(form.fields["prod"].initial)

    def test_prod_initial_is_all_products_if_prod_id_is_not_specified_in_constructor(self):
        form = ParProdForm()
        self.assertEqual(form.fields["prod"].queryset.count(), Prod.objects.count())

    def test_enum_val_queryset_is_enums(self,):
        form = ParProdForm()
        enums_count = Enums.objects.count()
        self.assertIsInstance(form.fields["enum_val"].queryset, QuerySet)
        self.assertEqual(form.fields["enum_val"].queryset.count(), enums_count)

    def test_prod_field_is_required(self):
        data = {
            "prod": None,
            "par": self.INT_PARAMETR,
            "enum_val": None,
            "int_value": None,
            "double_value": None,
        }
        expected_error_msg = ["Поле для изделия необходимо заполнить"]
        form = ParProdForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("prod", form.errors)
        self.assertEqual(
            form.errors["prod"], expected_error_msg
        )

    def test_par_field_is_required(self):
        data = {
            "prod": self.PRODUCT,
            "par": None,
            "enum_val": None,
            "int_value": None,
            "double_value": None,
        }
        expected_error_msg = ["Поле для параметра необходимо заполнить"]
        form = ParProdForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn("par", form.errors)
        self.assertEqual(
            form.errors["par"], expected_error_msg
        )

    def test_form_raises_validation_error_if_double_value_is_not_none_for_int_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": self.DOUBLE_VALUE,
            "enum_val": None,
        }
        form = ParProdForm(data)
        expected_error_msg = "Для целочисленного параметра нельзя указать значение поля double_value"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg,
        )

    def test_form_raises_validation_error_if_enum_val_is_not_none_for_int_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": None,
            "enum_val": self.ENUM_VAL
        }
        form = ParProdForm(data)
        expected_error_msg = "Для целочисленного параметра нельзя указать значение поля enum_val"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg,
        )

    def test_form_raises_validation_error_if_int_value_is_none_for_int_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_PARAMETR,
            "int_value": None,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data)
        expected_error_msg = "Для целочисленного параметра изделия необходимо указать значение поля int_value"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg
        )

    def test_form_does_not_raise_validation_error_if_given_int_value_is_within_the_range_for_int_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data)
        
        self.assertTrue(form.is_valid())

    def test_form_raises_validation_error_if_given_int_value_is_not_within_the_range_for_int_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_PARAMETR,
            "int_value": self.PARCLASS_INT_MIN_VALUE - 1,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            IntParErrors.INVALID_RANGE.format(
                int(self.PARCLASS_INT_MIN_VALUE),
                int(self.PARCLASS_INT_MAX_VALUE)
            ),
        )

    def test_form_raises_validation_error_if_int_value_is_not_none_for_double_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.DOUBLE_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": self.DOUBLE_VALUE,
            "enum_val": None,
        }
        form = ParProdForm(data)
        expected_error_msg = "Для вещественного параметра нельзя указать значение поля int_value"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg,
        )

    def test_form_raises_validation_error_if_enum_val_is_not_none_for_double_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.DOUBLE_PARAMETR,
            "int_value": None,
            "double_value": self.DOUBLE_VALUE,
            "enum_val": self.ENUM_VAL,
        }
        form = ParProdForm(data)
        expected_error_msg = "Для вещественного параметра нельзя указать значение поля enum_val"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg,
        )

    def test_form_raises_validation_error_if_double_value_is_none_for_double_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.DOUBLE_PARAMETR,
            "int_value": None,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data)
        expected_error_msg = "Для вещественного параметра изделия необходимо указать значение поля int_value"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg
        )

    def test_form_does_not_raise_validation_error_if_given_double_value_is_within_the_range_for_double_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.DOUBLE_PARAMETR,
            "int_value": None,
            "double_value": self.DOUBLE_VALUE,
            "enum_val": None,
        }
        form = ParProdForm(data)
        self.assertTrue(form.is_valid())

    def test_form_raises_validation_error_if_given_double_value_is_not_within_the_range_for_double_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.DOUBLE_PARAMETR,
            "int_value": None,
            "double_value": self.PARCLASS_DOUBLE_MAX_VALUE + 1,
            "enum_val": None,
        }
        form = ParProdForm(data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            DoubleParErrors.INVALID_RANGE.format(
                self.PARCLASS_DOUBLE_MIN_VALUE,
                self.PARCLASS_DOUBLE_MAX_VALUE
            ),
        )

    def test_form_raises_validation_error_if_double_value_was_specified_for_int_enum_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_ENUM_PARAMETR,
            "int_value": None,
            "double_value": self.DOUBLE_VALUE,
            "enum_val": self.ENUM_VAL,
        }
        form = ParProdForm(data)
        expected_error_msg = "Для параметра-перечисления изделия нельзя указать значение поля double_value"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg,
        )

    def test_form_raises_validation_error_if_int_value_was_specified_for_int_enum_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_ENUM_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": None,
            "enum_val": self.ENUM_VAL,
        }
        form = ParProdForm(data)
        expected_error_msg = "Для параметра-перечисления изделия нельзя указать значение поля int_value"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg,
        )

    def test_form_raises_validation_error_if_enum_val_is_none_for_int_enum_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_ENUM_PARAMETR,
            "int_value": None,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data)
        expected_error_msg = "Для параметра-перечисления изделия необходимо указать значение поля enum_val"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg
        )

    def test_form_does_not_raise_validation_error_if_double_and_int_value_are_not_specified_for_int_enum_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_ENUM_PARAMETR,
            "int_value": None,
            "double_value": None,
            "enum_val": self.ENUM_VAL,
        }
        form = ParProdForm(data)

        self.assertTrue(form.is_valid())

    def test_form_raises_validation_error_if_main_product_class_does_not_have_given_parametr(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INVALID_INT_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data)
        expected_error_msg = "Параметр 'parameter' не принадлежит классу изделия 'nuts_product_class'"

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            expected_error_msg
        )

    def test_correct_form_data_for_int_parametr_is_saved_correctly(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data)
        self.assertTrue(form.is_valid())

        instance = form.save()
        self.assertIsNotNone(instance.pk)

    def test_correct_form_data_for_double_parametr_is_saved_correctly(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.DOUBLE_PARAMETR,
            "int_value": None,
            "double_value": self.DOUBLE_VALUE,
            "enum_val": None,
        }
        form = ParProdForm(data)
        self.assertTrue(form.is_valid())

        instance = form.save()
        self.assertIsNotNone(instance.pk)

    def test_correct_form_data_for_enum_parametr_is_saved_correctly(self):
        data = {
            "prod": self.PRODUCT,
            "par": self.INT_ENUM_PARAMETR,
            "int_value": None,
            "double_value": None,
            "enum_val": self.ENUM_VAL,
        }
        form = ParProdForm(data)
        self.assertTrue(form.is_valid())

        instance = form.save()
        self.assertIsNotNone(instance.pk)

    def test_update_form_raises_validation_error_if_prod_field_is_none(self):
        instance = self._create_par_prod_instance()

        update_data = {
            "prod": None,
            "par": self.INT_PARAMETR,
            "int_value": self.INT_VALUE,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data=update_data, instance=instance)
        expected_error_msg = ["Поле для изделия необходимо заполнить"]

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["prod"],
            expected_error_msg
        )

    def test_update_form_raises_validation_error_if_par_field_is_none(self):
        instance = self._create_par_prod_instance()

        update_data = {
            "prod": self.PRODUCT,
            "par": None,
            "int_value": self.INT_VALUE,
            "double_value": None,
            "enum_val": None,
        }
        form = ParProdForm(data=update_data, instance=instance)
        expected_error_msg = ["Поле для параметра необходимо заполнить"]

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["par"],
            expected_error_msg
        )


class ModificationFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fake = Faker()

        cls.valid_data = {
            "name": cls.fake.name()[:ProdConsts.NAME_MAX_LENGTH],
            "short_name": cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]
        }
        cls.empty_name_data = {
            "name": "",
            "short_name": cls.fake.name()[:ProdConsts.SHORT_NAME_MAX_LENGTH]
        }

    def test_modification_form_is_valid(self):
        form = ModificationForm(self.valid_data)
        self.assertTrue(form.is_valid())

    def test_empty_name_raises_validation_error(self):
        form = ModificationForm(self.empty_name_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["name"],
            [ProdErrors.EMPTY_NAME_FIELD]
        )


class SearchFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.base_ei = Ei.objects.first()

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.int_par_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.int_enum_type = ClassStruct.objects.get(pk=EnumsIds.INT)

        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.faker.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.enum_subclass = ClassStruct.objects.create(
            name="enum class",
            short_name="class",
            main_class=cls.int_enum_type,
            base_ei=cls.base_ei,
        )

        cls.prod1 = Prod.objects.create(
            name="test prod1",
            short_name="prod1",
            class_field=cls.nuts_subclass,
            image=None,
            cost=200,
            modification=None,
            ei=cls.base_ei
        )
        cls.prod2 = Prod.objects.create(
            name="test prod2",
            short_name="prod2",
            class_field=cls.nuts_subclass,
            image=None,
            cost=200,
            modification=None,
            ei=cls.base_ei
        )

        cls.par1_name = "test parametr1"
        cls.par2_name = "test parametr2"

        cls.par1 = Parametr.objects.create(
            name=cls.par1_name,
            short_name="parametr1",
            parametr_type=cls.int_par_type,
            par_ei=cls.base_ei,
        )
        cls.par2 = Parametr.objects.create(
            name=cls.par2_name,
            short_name="parametr2",
            parametr_type=cls.int_enum_type,
            par_ei=cls.base_ei,
        )

        cls.enum1 = Enums.objects.create(
            enum=cls.enum_subclass,
            num=1,
            name=None,
            short_name=None,
            double_value=None,
            int_value=2,
            image=None,
        )
        cls.enum2 = Enums.objects.create(
            enum=cls.enum_subclass,
            num=2,
            name=None,
            short_name=None,
            double_value=None,
            int_value=4,
            image=None,
        )

        cls.parclass1 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            num=1,
            min_value=100,
            max_value=200
        )
        cls.parclass2 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par2,
            num=2,
            min_value=None,
            max_value=None
        )

        cls.parprod1_1 = ParProd.objects.create(
            prod=cls.prod1,
            par=cls.par1,
            int_value=150,
            double_value=None,
            enum_val=None,
        )
        cls.parprod1_2 = ParProd.objects.create(
            prod=cls.prod1,
            par=cls.par2,
            int_value=None,
            double_value=None,
            enum_val=cls.enum1,
        )

        cls.parprod2_1 = ParProd.objects.create(
            prod=cls.prod2,
            par=cls.par1,
            int_value=120,
            double_value=None,
            enum_val=None,
        )
        cls.parprod2_2 = ParProd.objects.create(
            prod=cls.prod2,
            par=cls.par2,
            int_value=None,
            double_value=None,
            enum_val=cls.enum2,
        )

        cls.form = SearchForm({}, cls=cls.nuts_subclass)

    def test_form_instance_has_correct_number_of_parameter_fields(self):
        self.assertEqual(len(self.form.fields), 2)

    def test_form_instance_has_correct_fields_names(self):
        self.assertEqual(list(self.form.fields.keys()), [self.par1_name, self.par2_name])

    def test_form_instance_has_correct_help_texts(self):
        self.assertEqual(
            self.form.fields[self.par1_name].help_text,
            f"""Вводить в формате "min-max" (например, "10.0-20.0").<br>Границы диапазоны: {100.0}-{200.0}"""
        )

    def test_form_instance_without_specified_fields_is_valid(self):
        self.assertTrue(self.form.is_valid(), self.form.errors)

    def test_form_instance_is_valid_if_fields_were_specified_correctly(self):
        self.form = SearchForm({
            self.par1_name: "150.0 - 160.0",
            self.par2_name: str(self.enum1.pk),
        }, cls=self.nuts_subclass)
        self.assertTrue(self.form.is_valid())

    def test_form_instance_is_invalid_if_numeric_field_is_incorrect(self):
        self.form = SearchForm({
            self.par1_name: "150.0 ; 160.0",
            self.par2_name: str(self.enum1.pk),
        }, cls=self.nuts_subclass)
        self.assertFalse(self.form.is_valid())

    def test_form_instance_enum_field_has_correct_queryset(self):
        self.assertQuerySetEqual(
            self.form.fields[self.par2_name].queryset,
            Enums.objects.filter(
                parprod__par=self.parclass2.parametr
            ).distinct(),
            ordered=False
        )
