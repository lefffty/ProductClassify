from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

from ei.models import Ei
from enums.models import Enums
from classes.models import ClassStruct, ParClass
from parametr.models import Parametr

from ..models import Prod, ParProd
from ..constants import INT_PARAMS, DOUBLE_PARAMS, ENUM_CLASSES_IDS, FASTENER_ID


class ProdModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.main_class = ClassStruct.objects.create(
            name="main_class",
            short_name="main_cl",
            base_ei=None,
            main_class=None,
        )

    def test_create_with_minimal_requirements(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod = Prod.objects.create(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=image,
        )
        self.assertIsNotNone(prod.pk)

    def test_string_representation(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod = Prod(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=image,
        )
        self.assertEqual(str(prod), "test")

    def test_image_field_path(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod = Prod.objects.create(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=image,
        )
        self.assertTrue(prod.image.name.startswith("product_images/"))

    def test_class_field_relation(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )
        prod = Prod.objects.create(
            name="test",
            short_name="test",
            class_field=self.main_class,
            image=image,
        )
        self.assertEqual(prod.class_field, self.main_class)
        self.assertIn(prod, self.main_class.class_products.all())


class ParProdModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        par_ei = Ei.objects.first()
        base_ei = Ei.objects.order_by("id")[1]
        fastener_class = ClassStruct.objects.get(pk=FASTENER_ID)
        class_field = ClassStruct.objects.create(
            name="products_class",
            short_name="prod_cls",
            base_ei=base_ei,
            main_class=fastener_class,
        )

        # типы параметров
        cls.int_parametr_type = ClassStruct.objects.get(pk=INT_PARAMS)
        cls.double_parametr_type = ClassStruct.objects.get(pk=DOUBLE_PARAMS)
        cls.string_enum_type = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[0])
        cls.image_enum_type = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[1])
        cls.double_enum_type = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[2])
        cls.int_enum_type = ClassStruct.objects.get(pk=ENUM_CLASSES_IDS[3])

        # классы перечислений
        cls.int_enum_class = ClassStruct.objects.create(
            name="int_enum_class",
            short_name="int_enum",
            base_ei=base_ei,
            main_class=cls.int_enum_type,
        )
        cls.double_enum_class = ClassStruct.objects.create(
            name="double_enum_class",
            short_name="double_enum",
            base_ei=base_ei,
            main_class=cls.double_enum_type,
        )
        cls.string_enum_class = ClassStruct.objects.create(
            name="string_enum_class",
            short_name="string_enum",
            base_ei=base_ei,
            main_class=cls.string_enum_type,
        )
        cls.image_enum_class = ClassStruct.objects.create(
            name="image_enum_class",
            short_name="image_enum",
            base_ei=base_ei,
            main_class=cls.image_enum_type,
        )

        # дополнительные переменные
        cls.image = SimpleUploadedFile(
            "test.jpg",
            b"content",
            content_type="image/jpeg",
        )

        cls.prod = Prod.objects.create(
            name="test_prod",
            short_name="test",
            class_field=class_field,
            image=cls.image,
        )

        # экземпляры параметров различных типов
        cls.int_parametr = Parametr.objects.create(
            name="int_parametr",
            short_name="int_par",
            parametr_type=cls.int_parametr_type,
            par_ei=par_ei,
        )
        cls.double_parametr = Parametr.objects.create(
            name="double_parametr",
            short_name="double_par",
            parametr_type=cls.double_parametr_type,
            par_ei=par_ei,
        )
        cls.string_enum_parametr = Parametr.objects.create(
            name="string_enum_parametr",
            short_name="str_enum_par",
            parametr_type=cls.string_enum_type,
            par_ei=par_ei,
        )
        cls.image_enum_parametr = Parametr.objects.create(
            name="image_enum_parametr",
            short_name="image_enum_par",
            parametr_type=cls.image_enum_type,
            par_ei=None,
        )
        cls.double_enum_parametr = Parametr.objects.create(
            name="double_enum_parametr",
            short_name="double_enum_par",
            parametr_type=cls.double_enum_type,
            par_ei=par_ei,
        )
        cls.int_enum_parametr = Parametr.objects.create(
            name="int_enum_parametr",
            short_name="int_enum_par",
            parametr_type=cls.int_enum_type,
            par_ei=par_ei,
        )
        cls.invalid_parametr = Parametr.objects.create(
            name="invalid_parametr",
            short_name="invalid_par",
            parametr_type=cls.int_parametr_type,
            par_ei=par_ei,
        )

        # значения перечислений
        cls.string_enum_value = Enums.objects.create(
            enum=cls.string_enum_class,
            num=1,
            name="string_enum_value",
            short_name="string_enum",
            double_value=None,
            int_value=None,
            image=None,
        )
        cls.image_enum_value = Enums.objects.create(
            enum=cls.image_enum_class,
            num=1,
            name="image_enum_value",
            short_name="string_enum",
            double_value=None,
            int_value=None,
            image=cls.image,
        )
        cls.int_enum_value = Enums.objects.create(
            enum=cls.int_enum_class,
            num=1,
            name="int_enum_value",
            short_name="int_enum",
            double_value=None,
            int_value=1,
            image=None,
        )
        cls.double_enum_value = Enums.objects.create(
            enum=cls.double_enum_class,
            num=1,
            name="double_enum_value",
            short_name="double_enum",
            double_value=1.0,
            int_value=None,
            image=None,
        )

        num = 1
        double_parametr_parclass = ParClass.objects.create(
            class_field=class_field,
            parametr=cls.double_parametr,
            num=num,
            min_value=1.0,
            max_value=5.0,
        )
        num += 1
        int_parametr_parclass = ParClass.objects.create(
            class_field=class_field,
            parametr=cls.int_parametr,
            num=num,
            min_value=1,
            max_value=5,
        )
        num += 1
        string_enum_parametr_parclass = ParClass.objects.create(
            class_field=class_field,
            parametr=cls.string_enum_parametr,
            num=num,
            min_value=None,
            max_value=None,
        )
        num += 1
        image_enum_parametr_parclass = ParClass.objects.create(
            class_field=class_field,
            parametr=cls.image_enum_parametr,
            num=num,
            min_value=None,
            max_value=None,
        )
        num += 1
        double_enum_parametr_parclass = ParClass.objects.create(
            class_field=class_field,
            parametr=cls.double_enum_parametr,
            num=num,
            min_value=None,
            max_value=None,
        )
        num += 1
        int_enum_parametr_parclass = ParClass.objects.create(
            class_field=class_field,
            parametr=cls.int_enum_parametr,
            num=num,
            min_value=None,
            max_value=None,
        )

    def test_clean_raises_validation_error_if_parametr_does_not_belong_to_product_class(
        self,
    ):
        """Проверяет, что при попытке добавить параметр, не принадлежащий классу изделия,
        выбрасывается ValidationError с соответствующим сообщением."""
        parprod = ParProd(
            prod=self.prod,
            par=self.invalid_parametr,
            int_value=1,
            double_value=None,
            enum_val=None,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Параметр 'invalid_parametr' не принадлежит классу изделия 'products_class'."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_string_enum_value_is_absent(self):
        """Проверяет, что для параметра типа 'Строковое перечисление' обязательно
        наличие выбранного значения перечисления (enum_val не должен быть None)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.string_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=None,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Строковое перечисление' необходимо выбрать значение из списка строковых перечислений."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_string_enum_value_does_not_belong_to_string_enum_class(
        self,
    ):
        """Проверяет, что для параметра типа 'Строковое перечисление' выбранное
        значение перечисления должно принадлежать именно строковому перечислению,
        а не другому типу (например, изображениям)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.string_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.image_enum_value,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Строковое перечисление' необходимо выбрать значение из списка строковых перечислений."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_image_enum_value_is_absent(self):
        """Проверяет, что для параметра типа 'Перечисление изображений' обязательно
        наличие выбранного значения перечисления (enum_val не должен быть None)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.image_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=None,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Перечисление изображений' необходимо выбрать значение из списка перечислений изображений."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_image_enum_value_does_not_belong_to_image_enum_class(
        self,
    ):
        """Проверяет, что для параметра типа 'Перечисление изображений' выбранное
        значение перечисления должно принадлежать именно перечислению изображений,
        а не другому типу (например, строковому)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.image_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.string_enum_value,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Перечисление изображений' необходимо выбрать значение из списка перечислений изображений."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_int_enum_value_is_absent(self):
        """Проверяет, что для параметра типа 'Целочисленное перечисление' обязательно
        наличие выбранного значения перечисления (enum_val не должен быть None)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.int_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=None,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Целочисленное перечисление' необходимо выбрать значение из списка целочисленных перечислений."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_int_enum_value_does_not_belong_to_int_enum_class(
        self,
    ):
        """Проверяет, что для параметра типа 'Целочисленное перечисление' выбранное
        значение перечисления должно принадлежать именно целочисленному перечислению,
        а не другому типу (например, изображениям)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.int_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.image_enum_value,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Целочисленное перечисление' необходимо выбрать значение из списка целочисленных перечислений."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_double_enum_value_is_absent(self):
        """Проверяет, что для параметра типа 'Вещественное перечисление' обязательно
        наличие выбранного значения перечисления (enum_val не должен быть None)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.double_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=None,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Вещественное перечисление' необходимо выбрать значение из списка вещественных перечислений."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_double_enum_value_does_not_belong_to_double_enum_class(
        self,
    ):
        """Проверяет, что для параметра типа 'Вещественное перечисление' выбранное
        значение перечисления должно принадлежать именно вещественному перечислению,
        а не другому типу (например, строковому)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.double_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.string_enum_value,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Вещественное перечисление' необходимо выбрать значение из списка вещественных перечислений."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_double_value_is_absent(self):
        """Проверяет, что для параметра типа 'Вещественное число' обязательно
        указать вещественное значение (double_value не должен быть None)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.double_parametr,
            int_value=None,
            double_value=None,
            enum_val=None,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Вещественное число' необходимо указать вещественное значение."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_clean_raises_validation_error_if_int_value_is_absent(self):
        """Проверяет, что для параметра типа 'Целое число' обязательно
        указать целочисленное значение (int_value не должен быть None)."""
        parprod = ParProd(
            prod=self.prod,
            par=self.int_parametr,
            int_value=None,
            double_value=None,
            enum_val=None,
        )
        with self.assertRaises(ValidationError) as ve:
            parprod.full_clean()
        expected_error_msg = "Для параметра типа 'Целое число' необходимо указать целочисленное значение."
        self.assertEqual(ve.exception.messages[0], expected_error_msg)

    def test_create_object_with_minimum_requirements(self):
        """Проверяет возможность создания объекта ParProd с минимально необходимыми
        полями (только для целочисленного параметра, остальные поля не обязательны)."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.int_parametr,
            int_value=1,
            double_value=None,
            enum_val=None,
        )
        self.assertIsNotNone(parprod.pk)

    def test_product_relationship(self):
        """Проверяет связь с моделью Prod: объект ParProd должен появляться
        в обратной связи product_params у соответствующего изделия."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.int_parametr,
            int_value=1,
            double_value=None,
            enum_val=None,
        )
        self.assertIn(parprod, self.prod.product_params.all())

    def test_parametr_relationship(self):
        """Проверяет связь с моделью Parametr: объект ParProd должен появляться
        в обратной связи parprod_set у соответствующего параметра."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.int_parametr,
            int_value=1,
            double_value=None,
            enum_val=None,
        )
        self.assertIn(parprod, self.int_parametr.parprod_set.all())

    def test_enum_val_relationship(self):
        """Проверяет связь с моделью Enums: объект ParProd должен корректно
        ссылаться на выбранное значение перечисления (enum_val)."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.int_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.int_enum_value,
        )
        self.assertIsNotNone(parprod.pk)

    def test_unique_constraint(self):
        """Проверяет, что ограничение уникальности (prod, par) работает:
        попытка создать второй объект с той же парой изделие-параметр вызывает IntegrityError.
        """
        ParProd.objects.create(
            prod=self.prod,
            par=self.int_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.int_enum_value,
        )
        with self.assertRaises(IntegrityError):
            ParProd.objects.create(
                prod=self.prod,
                par=self.int_enum_parametr,
                int_value=None,
                double_value=None,
                enum_val=self.int_enum_value,
            )

    def test_clean_valid_for_int_parametr(self):
        """Проверяет, что clean() не выбрасывает ошибку для корректного целочисленного параметра."""
        parprod = ParProd(
            prod=self.prod,
            par=self.int_parametr,
            int_value=5,
            double_value=None,
            enum_val=None,
        )
        # Не должно быть исключений
        parprod.full_clean()

    def test_clean_valid_for_double_parametr(self):
        """Проверяет, что clean() не выбрасывает ошибку для корректного вещественного параметра."""
        parprod = ParProd(
            prod=self.prod,
            par=self.double_parametr,
            int_value=None,
            double_value=3.14,
            enum_val=None,
        )
        parprod.full_clean()

    def test_clean_valid_for_string_enum(self):
        """Проверяет, что clean() не выбрасывает ошибку для корректного строкового перечисления."""
        parprod = ParProd(
            prod=self.prod,
            par=self.string_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.string_enum_value,
        )
        parprod.full_clean()

    def test_clean_valid_for_image_enum(self):
        """Проверяет, что clean() не выбрасывает ошибку для корректного перечисления изображений."""
        parprod = ParProd(
            prod=self.prod,
            par=self.image_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.image_enum_value,
        )
        parprod.full_clean()

    def test_clean_valid_for_int_enum(self):
        """Проверяет, что clean() не выбрасывает ошибку для корректного целочисленного перечисления."""
        parprod = ParProd(
            prod=self.prod,
            par=self.int_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.int_enum_value,
        )
        parprod.full_clean()

    def test_clean_valid_for_double_enum(self):
        """Проверяет, что clean() не выбрасывает ошибку для корректного вещественного перечисления."""
        parprod = ParProd(
            prod=self.prod,
            par=self.double_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.double_enum_value,
        )
        parprod.full_clean()

    def test_create_without_full_clean_does_not_validate(self):
        """Проверяет, что create() не вызывает clean(), и объект с невалидными данными может быть сохранён."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.string_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=None,
        )
        self.assertIsNotNone(parprod.pk)
        with self.assertRaises(ValidationError):
            parprod.full_clean()

    def test_string_representation_for_int_parametr(self):
        """Проверяет строковое представление для целочисленного параметра."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.int_parametr,
            int_value=5,
            double_value=None,
            enum_val=None,
        )
        expected = f"{self.prod.name} - {self.int_parametr.name} - 5"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_double_parametr(self):
        """Проверяет строковое представление для вещественного параметра."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.double_parametr,
            int_value=None,
            double_value=3.14,
            enum_val=None,
        )
        expected = f"{self.prod.name} - {self.double_parametr.name} - 3.14"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_int_enum_value(self):
        """Проверяет строковое представление для целочисленного перечисления."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.int_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.int_enum_value,
        )
        expected = f"{self.prod.name} - {self.int_enum_value.short_name} - {self.int_enum_value.int_value}"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_double_enum_value(self):
        """Проверяет строковое представление для вещественного перечисления."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.double_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.double_enum_value,
        )
        expected = f"{self.prod.name} - {self.double_enum_value.short_name} - {self.double_enum_value.double_value}"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_string_enum_value(self):
        """Проверяет строковое представление для строкового перечисления."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.string_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.string_enum_value,
        )
        expected = f"{self.prod.name} - {self.string_enum_value.name}"
        self.assertEqual(str(parprod), expected)

    def test_string_representation_for_image_enum_value(self):
        """Проверяет строковое представление для перечисления изображений."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.image_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.image_enum_value,
        )
        expected = f"{self.prod.name} - {self.image_enum_value.short_name}"
        self.assertEqual(str(parprod), expected)

    def test_get_value_for_int_parametr(self):
        """Проверяет, что get_value возвращает целочисленное значение."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.int_parametr,
            int_value=5,
            double_value=None,
            enum_val=None,
        )
        self.assertEqual(parprod.get_value(), 5)

    def test_get_value_for_double_parametr(self):
        """Проверяет, что get_value возвращает вещественное значение."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.double_parametr,
            int_value=None,
            double_value=3.14,
            enum_val=None,
        )
        self.assertEqual(parprod.get_value(), 3.14)

    def test_get_value_for_string_enum_value(self):
        """Проверяет, что get_value возвращает название для строкового перечисления."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.string_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.string_enum_value,
        )
        self.assertEqual(parprod.get_value(), self.string_enum_value.name)

    def test_get_value_for_int_enum_value(self):
        """Проверяет, что get_value возвращает целочисленное значение перечисления."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.int_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.int_enum_value,
        )
        self.assertEqual(parprod.get_value(), self.int_enum_value.int_value)

    def test_get_value_for_double_enum_value(self):
        """Проверяет, что get_value возвращает вещественное значение перечисления."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.double_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.double_enum_value,
        )
        self.assertEqual(parprod.get_value(), self.double_enum_value.double_value)

    def test_get_value_for_image_enum_value(self):
        """Проверяет, что get_value возвращает объект изображения для перечисления изображений."""
        parprod = ParProd.objects.create(
            prod=self.prod,
            par=self.image_enum_parametr,
            int_value=None,
            double_value=None,
            enum_val=self.image_enum_value,
        )
        self.assertEqual(parprod.get_value(), self.image_enum_value.image)
