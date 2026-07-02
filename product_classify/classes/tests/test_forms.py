from django.test import TestCase
from django.db.models import QuerySet

from unittest.mock import patch

from ei.models import Ei
from classes.models import ClassStruct
from classes.forms import ProdClassForm


class ProdClassFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()

        cls.root = ClassStruct.objects.create(
            name="Root",
            short_name="R",
            base_ei=cls.base_ei,
            main_class=None,
        )
        cls.child = ClassStruct.objects.create(
            name="Child",
            short_name="C",
            base_ei=cls.base_ei,
            main_class=cls.root,
        )
        cls.other = ClassStruct.objects.create(
            name="Other",
            short_name="O",
            base_ei=cls.base_ei,
            main_class=None,
        )

        cls.invalid_main_class = ClassStruct.objects.create(
            name="Test Main Class",
            short_name="Test Main Class",
            base_ei=cls.base_ei,
            main_class=None,
        )
        cls.valid_main_class = ClassStruct.objects.create(
            name="Test Class",
            short_name="Test Class",
            base_ei=Ei.objects.first(),
            main_class=cls.child,
        )
        cls.ei = Ei.objects.create(
            name="Test EI",
            short_name="Test EI",
            code="0007",
            convert_factor=1,
            main_class=None,
        )

    def test_main_class_queryset_is_terminal_product_classes(self):
        """Проверяет, что поле main_class в форме использует queryset из ClassStruct.terminal_product_classes()."""
        form = ProdClassForm()
        self.assertIsInstance(form.fields["main_class"].queryset, QuerySet)

    def test_base_ei_queryset_is_all_ei_objects(self):
        """Проверяет, что поле base_ei в форме использует queryset со всеми объектами Ei."""
        form = ProdClassForm()
        eis_count = Ei.objects.count()
        self.assertIsInstance(form.fields["base_ei"].queryset, QuerySet)
        self.assertEqual(form.fields["base_ei"].queryset.count(), eis_count)

    def test_check_class_struct_cycles_called_with_correct_params(self):
        """Проверяет, что метод _check_class_struct_cycles вызывается с правильными параметрами (cls_id и main_cls_id)."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            with patch.object(
                ProdClassForm,
                "_check_class_struct_cycles",
                return_value=False,
            ) as mock_check_class_struct_cycles:
                form_data = {
                    "name": self.root.name,
                    "short_name": self.root.short_name,
                    "main_class": self.other,
                    "base_ei": self.root.base_ei,
                }
                form = ProdClassForm(data=form_data, instance=self.root)
                self.assertTrue(form.is_valid())
                mock_check_class_struct_cycles.assert_called_once()
                call_args = mock_check_class_struct_cycles.call_args[0]
                first_arg_error = "cls_id должен быть равен id редактируемого объекта"
                second_arg_error = (
                    "main_cls_id должен быть равен id выбранного родителя"
                )
                self.assertEqual(
                    call_args[1],
                    self.root.pk,
                    first_arg_error,
                )
                self.assertEqual(
                    call_args[2],
                    self.other.pk,
                    second_arg_error,
                )

    def test_name_field_is_required(self):
        """Проверяет, что поле name обязательно для заполнения и выводится кастомное сообщение об ошибке."""
        form_data = {
            "name": "",
            "short_name": "Test Name",
            "main_class": self.valid_main_class,
            "base_ei": self.ei,
        }
        form = ProdClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"], ["Поле для названия класса необходимо заполнить"]
        )

    def test_main_class_field_is_required(self):
        """Проверяет, что поле main_class обязательно для заполнения и выводится кастомное сообщение об ошибке."""
        form_data = {
            "name": "Test Name",
            "short_name": "Test Name",
            "main_class": None,
            "base_ei": self.ei,
        }
        form = ProdClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(
            form.errors["main_class"],
            ["Поле для родительского класса необходимо заполнить"],
        )

    def test_non_terminal_main_class_is_invalid(self):
        """Проверяет, что выбор родительского класса, не входящего в терминальные классы, приводит к невалидности формы."""
        form_data = {
            "name": "Test Name",
            "short_name": "Test Name",
            "main_class": self.invalid_main_class,
            "base_ei": self.ei,
        }
        form = ProdClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_clean_raises_error_when_cycle_detected_while_editing_existing_record(self):
        """Проверяет, что при редактировании существующей записи и создании циклической ссылки форма невалидна и содержит ошибку о цикле."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.root.name,
                "short_name": self.root.short_name,
                "main_class": self.child,
                "base_ei": self.root.base_ei if self.root.base_ei else None,
            }
            form = ProdClassForm(data=form_data, instance=self.root)
            self.assertFalse(form.is_valid())
            self.assertIn("__all__", form.errors)
            expected_error_msg = (
                "При изменении класса в классификаторе образовывается цикл!"
            )
            self.assertEqual(
                form.errors["__all__"][0],
                expected_error_msg,
            )

    def test_clean_does_not_raise_error_when_no_cycle_while_editing_existing_record(
        self,
    ):
        """Проверяет, что при редактировании существующей записи без создания цикла форма валидна и объект сохраняется с новым родителем."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.root.name,
                "short_name": self.root.short_name,
                "main_class": self.other,
                "base_ei": self.root.base_ei if self.root.base_ei else None,
            }
            form = ProdClassForm(data=form_data, instance=self.root)
            self.assertTrue(form.is_valid())
            obj = form.save()
            self.assertEqual(obj.main_class, self.other)

    def test_clean_does_not_raise_error_when_no_cycle(self):
        """Проверяет, что при создании нового объекта без циклической ссылки форма валидна и объект сохраняется."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": "Test Name",
                "short_name": "Test Name",
                "main_class": self.root,
                "base_ei": self.ei,
            }
            form = ProdClassForm(data=form_data)
            self.assertTrue(form.is_valid())
            obj = form.save()
            self.assertEqual(obj.main_class, self.root)

    def test_edit_existing_record_updates_object(self):
        """Проверяет, что при редактировании существующей записи форма обновляет поля объекта, а не создаёт новый."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": "Test Name",
                "short_name": self.root.short_name,
                "main_class": self.other,
                "base_ei": self.root.base_ei if self.root.base_ei else None,
            }
            form = ProdClassForm(data=form_data, instance=self.root)
            self.assertTrue(form.is_valid())
            obj = form.save()
            self.assertEqual(obj.pk, self.root.pk)
            self.assertEqual(obj.name, "Test Name")

    def test_cycle_when_main_class_is_self(self):
        """Проверяет, что установка родительским классом самого себя приводит к ошибке цикла."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": "Test Name",
                "short_name": self.root.short_name,
                "main_class": self.root,
                "base_ei": self.root.base_ei if self.root.base_ei else None,
            }
            form = ProdClassForm(data=form_data, instance=self.root)
            self.assertFalse(form.is_valid())
            self.assertIn("__all__", form.errors)
            expected_error_msg = (
                "При изменении класса в классификаторе образовывается цикл!"
            )
            self.assertEqual(
                form.errors["__all__"][0],
                expected_error_msg,
            )

    def test_cycle_not_checked_for_new_object(self):
        """Проверяет, что для новых объектов (без instance.pk) проверка циклов не выполняется."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            with patch.object(
                ProdClassForm, "_check_class_struct_cycles"
            ) as mock_check_class_struct_cycles:
                form_data = {
                    "name": "Test Name",
                    "short_name": self.root.short_name,
                    "main_class": self.root,
                    "base_ei": self.root.base_ei if self.root.base_ei else None,
                }
                form = ProdClassForm(data=form_data)
                self.assertTrue(form.is_valid())
                mock_check_class_struct_cycles.assert_not_called()

    def test_short_name_is_optional(self):
        """Проверяет, что поле short_name необязательно (может быть None) и форма остаётся валидной."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": "Test Name",
                "short_name": None,
                "main_class": self.valid_main_class,
                "base_ei": self.ei.pk,
            }
            form = ProdClassForm(data=form_data)
            self.assertTrue(form.is_valid())

    def test_base_ei_is_optional(self):
        """Проверяет, что поле base_ei необязательно (может быть None) и форма остаётся валидной."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": "Test Name",
                "short_name": "Test Name",
                "main_class": self.valid_main_class,
                "base_ei": None,
            }
            form = ProdClassForm(data=form_data)
            self.assertTrue(form.is_valid())
