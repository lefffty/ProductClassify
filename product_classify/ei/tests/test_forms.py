from django.test import TestCase
from django.db.models import QuerySet

from ei.models import Ei
from ei.forms import EiForm


class EiFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.NEW_INSTANCE_MAIN_CLASS = Ei.objects.first()
        cls.NEW_INSTANCE_NAME = "Test name"
        cls.NEW_INSTANCE_SHORT_NAME = "Test"
        cls.NEW_INSTANCE_CODE = "00000"
        cls.NEW_INSTANCE_CONVERT_FACTOR = 0.25
        cls.NEW_INSTANCE_INVALID_CONVERT_FACTOR = -0.25

        cls.ei_to_update = Ei.objects.last()

    def test_ei_queryset_is_ei_objects(self):
        """Проверяет, что поле main_class в форме использует queryset со всеми объектами Ei."""
        form = EiForm()
        self.assertIsInstance(form.fields["main_class"].queryset, QuerySet)
        self.assertEqual(len(form.fields["main_class"].queryset), Ei.objects.count())

    def test_name_is_required(self):
        """Проверяет, что поле name обязательно для заполнения."""
        form_data = {
            "name": None,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        expected_error_msg = "Поле названия единицы измерения необходимо заполнить"
        form = EiForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], [expected_error_msg])

    def test_short_name_is_required(self):
        """Проверяет, что поле short_name обязательно для заполнения."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": None,
            "code": self.NEW_INSTANCE_CODE,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        expected_error_msg = (
            "Поле сокращенного названия единицы измерения необходимо заполнить"
        )
        form = EiForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("short_name", form.errors)
        self.assertEqual(form.errors["short_name"], [expected_error_msg])

    def test_convert_factor_is_required(self):
        """Проверяет, что поле convert_factor обязательно для заполнения."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": None,
        }
        expected_error_msg = "Поле множителя для перевода в другую единицу измерения необходимо заполнить"
        form = EiForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("convert_factor", form.errors)
        self.assertEqual(form.errors["convert_factor"], [expected_error_msg])

    def test_main_class_is_optional(self):
        """Проверяет, что поле main_class может быть пустым (None) и форма остаётся валидной."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "main_class": None,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_code_is_optional(self):
        """Проверяет, что поле code может быть пустым (None или пустая строка) и форма остаётся валидной."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": None,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_raises_validation_error_if_convert_factor_is_lte_zero(self):
        """Проверяет, что значение convert_factor меньше минимально допустимого вызывает ошибку валидации."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": self.NEW_INSTANCE_INVALID_CONVERT_FACTOR,
        }
        form = EiForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("convert_factor", form.errors)

    def test_correct_form_instance_with_minimal_requirements_is_saved_correctly(self):
        """Проверяет, что форма с минимально необходимыми данными (name, short_name, convert_factor) сохраняет объект."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": None,
            "main_class": None,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)

    def test_form_is_valid_with_all_valid_data(self):
        """Проверяет, что форма с полностью корректными данными проходит валидацию."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_correct_form_instance_is_saved_correctly(self):
        """Проверяет, что форма с полностью заполненными валидными данными сохраняет объект со всеми полями."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        form = EiForm(data=form_data)
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.code, form_data["code"])
        self.assertEqual(obj.main_class, form_data["main_class"])
        self.assertEqual(obj.convert_factor, form_data["convert_factor"])

    def test_form_displays_all_validation_errors(self):
        """Проверяет, что при невалидных данных форма выводит все ошибки одновременно (для всех полей)."""
        form_data = {
            "name": "",
            "short_name": "",
            "code": "",
            "main_class": "",
            "convert_factor": "",
        }
        expected_errors = {
            "name": "Поле названия единицы измерения необходимо заполнить",
            "short_name": "Поле сокращенного названия единицы измерения необходимо заполнить",
            "convert_factor": "Поле множителя для перевода в другую единицу измерения необходимо заполнить",
        }

        form = EiForm(data=form_data)
        self.assertFalse(form.is_valid())

        for key, value in expected_errors.items():
            self.assertIn(key, form.errors)
            self.assertEqual(value, form.errors[key][0])

    def test_update_existing_instance(self):
        """Проверяет, что при редактировании существующей записи форма обновляет поля объекта."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        form = EiForm(data=form_data, instance=self.ei_to_update)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.code, form_data["code"])
        self.assertEqual(obj.main_class, form_data["main_class"])
        self.assertEqual(obj.convert_factor, form_data["convert_factor"])

    def test_save_with_empty_code(self):
        """Проверяет, что поле code может быть пустой строкой и корректно сохраняется."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": "",
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
        }
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.code, "")

    def test_update_without_changing_main_class(self):
        """Проверяет, что при редактировании без изменения main_class значение сохраняется."""
        ei = Ei.objects.create(
            name="Test",
            short_name="Test",
            code="Test",
            convert_factor=self.NEW_INSTANCE_CONVERT_FACTOR,
            main_class=self.NEW_INSTANCE_MAIN_CLASS,
        )

        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
            "main_class": self.NEW_INSTANCE_MAIN_CLASS,
        }
        form = EiForm(data=form_data, instance=ei)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.main_class, ei.main_class)

    def test_save_with_main_class_none(self):
        """Проверяет, что при сохранении объекта с main_class=None поле в БД равно NULL."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "code": self.NEW_INSTANCE_CODE,
            "convert_factor": self.NEW_INSTANCE_CONVERT_FACTOR,
            "main_class": None,
        }
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNone(obj.main_class)
