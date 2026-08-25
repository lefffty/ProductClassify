from tests.unit.base import BaseUnitTestCase
from django.db.models import QuerySet

from unittest.mock import patch

from classes.models import ClassStruct
from classes.constants import EnumsIds, ParamIds
from ei.models import Ei

from parametr.forms import ParametrForm


class ParametrFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.string_enum_type = ClassStruct.objects.get(pk=EnumsIds.STRING)
        cls.int_enum_type = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.double_enum_type = ClassStruct.objects.get(pk=EnumsIds.DOUBLE)
        cls.image_enum_type = ClassStruct.objects.get(pk=EnumsIds.IMAGE)
        cls.int_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.double_type = ClassStruct.objects.get(pk=ParamIds.DOUBLE)
        cls.agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)

        cls.par_ei = Ei.objects.first()
        cls.NAME = "Test name"
        cls.SHORT_NAME = "Test short name"
        cls.NEW_NAME = "New test name"
        cls.NEW_SHORT_NAME = "New short name"

    def test_parametr_type_queryset_are_parametr_types(self):
        """Проверяет, что поле parametr_type использует queryset с объектами ClassStruct.parametr_types()."""
        form = ParametrForm()
        self.assertIsInstance(form.fields["parametr_type"].queryset, QuerySet)

    def test_par_ei_queryset_are_ei_objects(self):
        """Проверяет, что поле par_ei использует queryset со всеми объектами Ei."""
        form = ParametrForm()
        expected_no_ei = Ei.objects.count()
        self.assertIsInstance(form.fields["par_ei"].queryset, QuerySet)
        self.assertEqual(len(form.fields["par_ei"].queryset), expected_no_ei)

    def test_parametr_type_is_required(self):
        """Проверяет, что поле parametr_type обязательно для заполнения."""
        form_data = {
            "parametr_type": None,
            "par_ei": self.par_ei,
            "name": "",
            "short_name": "",
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_name_is_required(self):
        """Проверяет, что поле name обязательно для заполнения."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": "",
            "short_name": "",
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_par_ei_is_optional(self):
        """Проверяет, что поле par_ei может быть None и форма проходит валидацию."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_short_name_is_optional_accepts_empty_string(self):
        """Проверяет, что поле short_name не может быть пустой строкой и форма не проходит валидацию."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": "",
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_short_name_is_optional_accepts_none(self):
        """Проверяет, что поле short_name не может быть равно None и не форма проходит валидацию."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": None,
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_string_enum_parametr_par_ei_is_none_does_not_raise_validation_error(self):
        """Проверяет, что для строкового перечисления отсутствие par_ei не вызывает ошибку валидации."""
        form_data = {
            "parametr_type": self.string_enum_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_string_enum_parametr_par_ei_is_not_none_raises_validation_error(self):
        """Проверяет, что для строкового перечисления указание par_ei вызывает ошибку валидации."""
        form_data = {
            "parametr_type": self.string_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_img_enum_parametr_par_ei_is_not_none_raises_validation_error(self):
        """Проверяет, что для перечисления изображений указание par_ei вызывает ошибку валидации."""
        form_data = {
            "parametr_type": self.image_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_img_enum_parametr_par_ei_is_none_does_not_raise_validation_error(self):
        """Проверяет, что для перечисления изображений отсутствие par_ei не вызывает ошибку валидации."""
        form_data = {
            "parametr_type": self.image_enum_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_double_enum_parametr_par_ei_is_none_does_not_raise_validation_error(self):
        """Проверяет, что для вещественного перечисления отсутствие par_ei не вызывает ошибку."""
        form_data = {
            "parametr_type": self.double_enum_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_double_enum_parametr_par_ei_is_not_none_does_not_raise_validation_error(
        self,
    ):
        """Проверяет, что для вещественного перечисления указание par_ei допустимо и не вызывает ошибку."""
        form_data = {
            "parametr_type": self.double_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_int_enum_parametr_par_ei_is_none_does_not_raise_validation_error(self):
        """Проверяет, что для целочисленного перечисления отсутствие par_ei не вызывает ошибку."""
        form_data = {
            "parametr_type": self.int_enum_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_int_enum_parametr_par_ei_is_not_none_does_not_raise_validation_error(self):
        """Проверяет, что для целочисленного перечисления указание par_ei допустимо."""
        form_data = {
            "parametr_type": self.int_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_int_parametr_par_ei_is_not_none_does_not_raise_validation_error(self):
        """Проверяет, что для целочисленного параметра указание par_ei допустимо."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_int_parametr_par_ei_is_none_does_not_raise_validation_error(self):
        """Проверяет, что для целочисленного параметра отсутствие par_ei допустимо."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_double_parametr_par_ei_is_none_does_not_raise_validation_error(self):
        """Проверяет, что для вещественного параметра отсутствие par_ei допустимо."""
        form_data = {
            "parametr_type": self.double_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_double_parametr_par_ei_is_not_none_does_not_raise_validation_error(self):
        """Проверяет, что для вещественного параметра указание par_ei допустимо."""
        form_data = {
            "parametr_type": self.double_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_agregat_parametr_par_ei_is_none_does_not_raise_validation_error(self):
        """Проверяет, что для агрегата отсутствие par_ei не вызывает ошибку валидации."""
        form_data = {
            "parametr_type": self.agregat_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_agregat_parametr_par_ei_is_not_none_raises_validation_error(self):
        """Проверяет, что для агрегата указание par_ei вызывает ошибку валидации."""
        form_data = {
            "parametr_type": self.agregat_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_string_enum_parametr_data_is_valid(self):
        """Проверяет, что форма для строкового перечисления с корректными данными проходит валидацию."""
        form_data = {
            "parametr_type": self.string_enum_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_string_enum_parametr_is_saved_correctly(self):
        """Проверяет, что объект строкового перечисления корректно сохраняется."""
        form_data = {
            "parametr_type": self.string_enum_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.parametr_type, form_data["parametr_type"])
        self.assertEqual(obj.par_ei, form_data["par_ei"])

    def test_image_enum_parametr_data_is_valid(self):
        """Проверяет, что форма для перечисления изображений с корректными данными проходит валидацию."""
        form_data = {
            "parametr_type": self.image_enum_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_image_enum_parametr_is_saved_correctly(self):
        """Проверяет, что объект перечисления изображений корректно сохраняется."""
        form_data = {
            "parametr_type": self.image_enum_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.parametr_type, form_data["parametr_type"])
        self.assertEqual(obj.par_ei, form_data["par_ei"])

    def test_agregat_parametr_data_is_valid(self):
        """Проверяет, что форма для агрегата с корректными данными проходит валидацию."""
        form_data = {
            "parametr_type": self.agregat_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_agregat_parametr_is_saved_correctly(self):
        """Проверяет, что объект агрегата корректно сохраняется."""
        form_data = {
            "parametr_type": self.agregat_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.parametr_type, form_data["parametr_type"])
        self.assertEqual(obj.par_ei, form_data["par_ei"])

    def test_int_enum_parametr_data_is_valid(self):
        """Проверяет, что форма для целочисленного перечисления с корректными данными проходит валидацию."""
        form_data = {
            "parametr_type": self.int_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_int_enum_parametr_is_saved_correctly(self):
        """Проверяет, что объект целочисленного перечисления корректно сохраняется."""
        form_data = {
            "parametr_type": self.int_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.parametr_type, form_data["parametr_type"])
        self.assertEqual(obj.par_ei, form_data["par_ei"])

    def test_double_enum_parametr_data_is_valid(self):
        """Проверяет, что форма для вещественного перечисления с корректными данными проходит валидацию."""
        form_data = {
            "parametr_type": self.double_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_double_enum_parametr_is_saved_correctly(self):
        """Проверяет, что объект вещественного перечисления корректно сохраняется."""
        form_data = {
            "parametr_type": self.double_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.parametr_type, form_data["parametr_type"])
        self.assertEqual(obj.par_ei, form_data["par_ei"])

    def test_double_parametr_data_is_valid(self):
        """Проверяет, что форма для вещественного параметра с корректными данными проходит валидацию."""
        form_data = {
            "parametr_type": self.double_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_double_parametr_is_saved_correctly(self):
        """Проверяет, что объект вещественного параметра корректно сохраняется."""
        form_data = {
            "parametr_type": self.double_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.parametr_type, form_data["parametr_type"])
        self.assertEqual(obj.par_ei, form_data["par_ei"])

    def test_int_parametr_data_is_valid(self):
        """Проверяет, что форма для целочисленного параметра с корректными данными проходит валидацию."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_int_parametr_is_saved_correctly(self):
        """Проверяет, что объект целочисленного параметра корректно сохраняется."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.name, form_data["name"])
        self.assertEqual(obj.short_name, form_data["short_name"])
        self.assertEqual(obj.parametr_type, form_data["parametr_type"])
        self.assertEqual(obj.par_ei, form_data["par_ei"])

    def test_parametr_type_relationship(self):
        """Проверяет, что объект связывается с правильным parametr_type через обратную связь."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()

        self.assertIn(obj, self.int_type.type_parameters.all())

    def test_par_ei_relationship(self):
        """Проверяет, что объект связывается с правильной par_ei через обратную связь."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()

        self.assertIn(obj, self.par_ei.parametr_set.all())

    def test_edit_parametr_is_updated_correctly(self):
        """Проверяет, что при редактировании существующего объекта все поля обновляются корректно."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()

        new_form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NEW_NAME,
            "short_name": self.NEW_SHORT_NAME,
        }
        form = ParametrForm(data=new_form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()

        self.assertEqual(obj.name, new_form_data["name"])
        self.assertEqual(obj.short_name, new_form_data["short_name"])
        self.assertEqual(obj.parametr_type, new_form_data["parametr_type"])
        self.assertEqual(obj.par_ei, new_form_data["par_ei"])

    def test_parametr_type_queryset_uses_parametr_types_method(self):
        """Проверяет, что queryset для parametr_type формируется через вызов ClassStruct.parametr_types()."""
        with patch("classes.models.ClassStruct.parametr_types") as mock_method:
            mock_method.return_value = ClassStruct.objects.none()
            _ = ParametrForm()
            mock_method.assert_called_once()

    def test_invalid_parametr_type_not_in_queryset_raises_error(self):
        """Проверяет, что выбор parametr_type, не входящего в parametr_types, вызывает ошибку валидации."""
        invalid_type = ClassStruct.objects.create(
            name="Invalid", short_name="Inv", main_class=None
        )
        form_data = {
            "parametr_type": invalid_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("parametr_type", form.errors)

    def test_string_enum_par_ei_error_message(self):
        """Проверяет, что при указании par_ei для строкового перечисления выводится корректное сообщение об ошибке."""
        form_data = {
            "parametr_type": self.string_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        expected_msg = (
            "Параметр типа 'Перечисление строк' не может иметь единиц измерения"
        )
        self.assertEqual(form.errors["__all__"][0], expected_msg)

    def test_edit_parametr_change_type_to_string_enum_with_par_ei_raises_error(self):
        """Проверяет, что при редактировании, если изменить тип на строковое перечисление и оставить par_ei, возникает ошибка."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()

        new_form_data = {
            "parametr_type": self.string_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=new_form_data, instance=obj)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_edit_parametr_remove_par_ei_for_allowed_type(self):
        """Проверяет, что при редактировании можно убрать par_ei для типа, который его допускает."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()

        new_form_data = {
            "parametr_type": self.int_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=new_form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNone(obj.par_ei)

    def test_edit_parametr_add_par_ei_for_allowed_type(self):
        """Проверяет, что при редактировании можно добавить par_ei для типа, который его допускает."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()

        new_form_data = {
            "parametr_type": self.int_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=new_form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.par_ei, self.par_ei)

    def test_edit_parametr_change_type_to_allowed_with_par_ei(self):
        """Проверяет, что при редактировании смены типа на другой разрешённый с сохранением par_ei форма валидна."""
        form_data = {
            "parametr_type": self.double_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        obj = form.save()

        new_form_data = {
            "parametr_type": self.int_enum_type,
            "par_ei": self.par_ei,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=new_form_data, instance=obj)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.parametr_type, self.int_enum_type)
        self.assertEqual(obj.par_ei, self.par_ei)

    def test_minimal_object_saved_without_short_name(self):
        """Проверяет, что объект с минимальными данными (parametr_type, name) и short_name=None сохраняется корректно."""
        form_data = {
            "parametr_type": self.int_type,
            "par_ei": None,
            "name": self.NAME,
            "short_name": self.SHORT_NAME,
        }
        form = ParametrForm(data=form_data)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.short_name, self.SHORT_NAME)
