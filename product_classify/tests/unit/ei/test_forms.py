from parameterized import parameterized
from django.db.models import QuerySet

from ei.models import Ei
from ei.errors import EiErrors
from ei.forms import EiForm

from tests.unit.base import BaseUnitTestCase
from tests.unit.ei.factories.ei import EiFormDataFactory, ChildEiFactory


class EiFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ei = Ei.objects.first()
        cls.ei_to_update = Ei.objects.last()

    def test_ei_queryset_is_ei_objects(self):
        """Проверяет, что поле main_class в форме использует queryset со всеми объектами Ei."""
        form = EiForm()
        self.assertIsInstance(form.fields["main_class"].queryset, QuerySet)
        self.assertEqual(len(form.fields["main_class"].queryset), Ei.objects.count())

    @parameterized.expand(
        [
            (None, "Test", "00000", Ei.objects.first(), 0.25, False, EiErrors.EMPTY_NAME, "name"),
            ("Test name", None, "00000", Ei.objects.first(), 0.25, False, EiErrors.EMPTY_SHORT_NAME, "short_name"),
            ("Test name", "Test", "00000", Ei.objects.first(), None, False, EiErrors.EMPTY_FACTOR, "convert_factor"),
            ("Test name", "Test", None, Ei.objects.first(), 0.25, True, None, None),
            ("Test name", "Test", "00000", None, 0.25, True, None, None),
        ],
    )
    def test_form_fields_are_required_or_not(
        self,
        name,
        short_name,
        code,
        main_class,
        convert_factor,
        is_valid,
        expected_error_msg,
        field_name,
    ):
        form_data = {
            "name": name,
            "short_name": short_name,
            "code": code,
            "main_class": main_class,
            "convert_factor": convert_factor,
        }
        form = EiForm(data=form_data)
        self.assertEqual(form.is_valid(), is_valid)
        if not is_valid:
            self.assertIn(field_name, form.errors)
            self.assertEqual(form.errors[field_name], [expected_error_msg])

    def test_raises_validation_error_if_convert_factor_is_lte_zero(self):
        """Проверяет, что значение convert_factor меньше минимально допустимого вызывает ошибку валидации."""
        convert_factor = -1
        form_data = EiFormDataFactory(convert_factor=convert_factor)
        form = EiForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("convert_factor", form.errors)

    def test_correct_form_instance_with_minimal_requirements_is_saved_correctly(self):
        """Проверяет, что форма с минимально необходимыми данными (name, short_name, convert_factor) сохраняет объект."""
        form_data = EiFormDataFactory(code=None, main_class=None)
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)

    def test_form_is_valid_with_all_valid_data(self):
        """Проверяет, что форма с полностью корректными данными проходит валидацию."""
        form_data = EiFormDataFactory()
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_correct_form_instance_is_saved_correctly(self):
        """Проверяет, что форма с полностью заполненными валидными данными сохраняет объект со всеми полями."""
        form_data = EiFormDataFactory()
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
        form_data = EiFormDataFactory(name="", short_name="", convert_factor="")
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
        form_data = EiFormDataFactory()
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
        form_data = EiFormDataFactory(code="")
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.code, "")

    def test_update_without_changing_main_class(self):
        """Проверяет, что при редактировании без изменения main_class значение сохраняется."""
        ei = ChildEiFactory(main_class=self.ei)
        form_data = EiFormDataFactory(main_class=self.ei_to_update.pk)
        form = EiForm(data=form_data, instance=ei)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.main_class, ei.main_class)

    def test_save_with_main_class_none(self):
        """Проверяет, что при сохранении объекта с main_class=None поле в БД равно NULL."""
        form_data = EiFormDataFactory()
        form = EiForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNone(obj.main_class)

    def test_save_with_main_class_causes_cycle_detection_and_raises_exception(self):
        form_data = EiFormDataFactory(main_class=2)
        form = EiForm(data=form_data, instance=self.ei)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(form.errors["main_class"], [EiErrors.CYCLE_DETECTED])

    def test_save_with_main_class_does_not_raise_exception(self):
        form_data = EiFormDataFactory()
        form = EiForm(data=form_data, instance=self.ei)
        self.assertTrue(form.is_valid())
