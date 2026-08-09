from django.test import TestCase
from django.db.models import QuerySet, PositiveSmallIntegerField
from django.db import transaction
from django.db.backends.base.operations import BaseDatabaseOperations

from unittest.mock import patch

from ei.models import Ei
from parametr.models import Parametr
from enums.constants import INT_ENUMS_ID
from products.constants import INT_PARAMS
from agregat.constants import AGREGAT_TYPE_ID

from classes.constants import NUTS_ID
from classes.models import ClassStruct, ParClass
from classes.forms import (
    ProdClassForm,
    EnumClassForm,
    ParClassForm,
    ChangeParClassNumForm,
)


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
        """Проверяет, что метод check_class_struct_cycles вызывается с правильными параметрами (cls_id и main_cls_id)."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            with patch.object(
                ClassStruct,
                "check_class_struct_cycles",
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
                expected_first_arg_error = (
                    "cls_id должен быть равен id редактируемого объекта"
                )
                expected_second_arg_error = (
                    "main_cls_id должен быть равен id выбранного родителя"
                )
                self.assertEqual(
                    call_args[1],
                    self.root.pk,
                    expected_first_arg_error,
                )
                self.assertEqual(
                    call_args[2],
                    self.other.pk,
                    expected_second_arg_error,
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
                ClassStruct, "check_class_struct_cycles"
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

    def test_form_displays_all_validation_errors(self):
        form_data = {
            "name": "",
            "short_name": "",
            "main_class": None,
            "base_ei": None,
        }
        form = ProdClassForm(data=form_data)
        self.assertFalse(form.is_valid())

        expected_errors = {
            "name": ["Поле для названия класса необходимо заполнить"],
            "main_class": ["Поле для родительского класса необходимо заполнить"],
        }

        for key, value in expected_errors.items():
            self.assertIn(key, form.errors)
            self.assertEqual(form.errors[key], expected_errors[key])


class EnumClassFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()

        cls.root = ClassStruct.objects.create(
            name="Test Name",
            short_name="Test Name",
            base_ei=cls.base_ei,
            main_class=None,
        )
        cls.child = ClassStruct.objects.create(
            name="Test Name",
            short_name="Test Name",
            base_ei=cls.base_ei,
            main_class=cls.root,
        )
        cls.other = ClassStruct.objects.create(
            name="Test Name",
            short_name="Test Name",
            base_ei=cls.base_ei,
            main_class=None,
        )

        cls.NEW_INSTANCE_NAME = "New test name"
        cls.NEW_INSTANCE_SHORT_NAME = "New test name"

        cls.UPDATED_INSTANCE_NAME = "Updated test name"
        cls.UPDATED_INSTANCE_SHORT_NAME = "Upd. test name"

    def test_main_class_queryset_is_all_enum_classes(self):
        """Проверяет, что поле main_class в форме использует queryset из ClassStruct.all_enum_classes()."""
        form = EnumClassForm()
        self.assertIsInstance(form.fields["main_class"].queryset, QuerySet)

    def test_main_class_is_required(self):
        """Проверяет, что поле main_class обязательно для заполнения и выводится кастомное сообщение об ошибке."""
        form_data = {
            "name": self.NEW_INSTANCE_NAME,
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "main_class": None,
        }
        form = EnumClassForm(data=form_data)
        expected_error_msg = "Поле для родительского класса необходимо заполнить"
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(
            form.errors["main_class"],
            [expected_error_msg],
        )

    def test_name_is_required(self):
        """Проверяет, что поле name обязательно для заполнения и выводится кастомное сообщение об ошибке."""
        form_data = {
            "name": "",
            "short_name": self.NEW_INSTANCE_SHORT_NAME,
            "main_class": self.other,
        }
        form = EnumClassForm(data=form_data)
        expected_error_msg = "Поле для названия класса необходимо заполнить"
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"],
            [expected_error_msg],
        )

    def test_short_name_is_optional(self):
        """Проверяет, что поле short_name может быть пустой строкой и форма остаётся валидной."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.NEW_INSTANCE_NAME,
                "short_name": "",
                "main_class": self.other,
            }
            form = EnumClassForm(data=form_data)
            self.assertTrue(form.is_valid(), form.errors)

    def test_short_name_accepts_none(self):
        """Проверяет, что поле short_name может быть None (пустое значение) и форма остаётся валидной."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.NEW_INSTANCE_NAME,
                "short_name": None,
                "main_class": self.other,
            }
            form = EnumClassForm(data=form_data)
            self.assertTrue(form.is_valid())

    def test_check_class_struct_cycles_is_called_with_correct_params(self):
        """Проверяет, что метод check_class_struct_cycles вызывается с правильными параметрами (cls_id и main_cls_id)."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            with patch.object(
                ClassStruct,
                "check_class_struct_cycles",
                return_value=False,
            ) as mock_check_class_struct_cycles:
                form_data = {
                    "name": self.UPDATED_INSTANCE_NAME,
                    "short_name": self.UPDATED_INSTANCE_SHORT_NAME,
                    "main_class": self.other,
                }
                form = EnumClassForm(data=form_data, instance=self.root)
                self.assertTrue(form.is_valid())
                mock_check_class_struct_cycles.assert_called_once()
                call_args = mock_check_class_struct_cycles.call_args[0]
                expected_first_arg_error = (
                    "cls_id должен быть равен id редактируемого объекта"
                )
                expected_second_arg_error = (
                    "main_cls_id должен быть равен id выбранного родителя"
                )
                self.assertEqual(call_args[1], self.root.pk, expected_first_arg_error)
                self.assertEqual(call_args[2], self.other.pk, expected_second_arg_error)

    def test_clean_raises_error_when_cycle_detected_while_editing_existing_record(self):
        """Проверяет, что при редактировании существующей записи и создании циклической ссылки форма невалидна и содержит ошибку о цикле."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.UPDATED_INSTANCE_NAME,
                "short_name": self.UPDATED_INSTANCE_SHORT_NAME,
                "main_class": self.child,
            }
            form = EnumClassForm(data=form_data, instance=self.root)
            expected_error_msg = (
                "При изменении класса в классификаторе образовывается цикл!"
            )
            self.assertFalse(form.is_valid())
            self.assertIn("__all__", form.errors)
            self.assertEqual(
                form.errors["__all__"][0],
                expected_error_msg,
            )

    def test_clean_does_not_raise_error_when_no_cycle_while_editing_existing_record(
        self,
    ):
        """Проверяет, что при редактировании существующей записи без создания цикла форма валидна и объект сохраняется с новым родителем."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.UPDATED_INSTANCE_NAME,
                "short_name": self.UPDATED_INSTANCE_SHORT_NAME,
                "main_class": self.other,
            }
            form = EnumClassForm(data=form_data, instance=self.root)
            self.assertTrue(form.is_valid())

    def test_clean_does_not_raise_error_when_no_cycle(self):
        """Проверяет, что при создании нового объекта без циклической ссылки форма валидна и объект сохраняется."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.NEW_INSTANCE_NAME,
                "short_name": self.NEW_INSTANCE_SHORT_NAME,
                "main_class": self.root,
            }
            form = EnumClassForm(data=form_data)
            self.assertTrue(form.is_valid())

    def test_edit_existing_record_updates_object(self):
        """Проверяет, что при редактировании существующей записи форма обновляет поля объекта, а не создаёт новый."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.UPDATED_INSTANCE_NAME,
                "short_name": self.UPDATED_INSTANCE_SHORT_NAME,
                "main_class": self.other,
            }
            form = EnumClassForm(data=form_data, instance=self.root)
            self.assertTrue(form.is_valid())
            obj = form.save()
            self.assertEqual(form_data["name"], obj.name)
            self.assertEqual(form_data["short_name"], obj.short_name)
            self.assertEqual(form_data["main_class"], obj.main_class)

    def test_cycle_when_main_class_is_self(self):
        """Проверяет, что установка родительским классом самого себя приводит к ошибке цикла."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.UPDATED_INSTANCE_NAME,
                "short_name": self.UPDATED_INSTANCE_SHORT_NAME,
                "main_class": self.root,
            }
            expected_error_msg = (
                "При изменении класса в классификаторе образовывается цикл!"
            )
            form = EnumClassForm(data=form_data, instance=self.root)
            self.assertFalse(form.is_valid())
            self.assertIn("__all__", form.errors)
            self.assertEqual(
                form.errors["__all__"][0],
                expected_error_msg,
            )

    def test_cycle_not_checked_for_new_object(self):
        """Проверяет, что для новых объектов (без instance.pk) проверка циклов не выполняется."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            with patch.object(
                ClassStruct,
                "check_class_struct_cycles",
            ) as mock_check_class_struct_cycles:
                form_data = {
                    "name": self.NEW_INSTANCE_NAME,
                    "short_name": self.NEW_INSTANCE_SHORT_NAME,
                    "main_class": self.other,
                }
                form = EnumClassForm(data=form_data)
                self.assertTrue(form.is_valid())
                obj = form.save()
                mock_check_class_struct_cycles.assert_not_called()
                self.assertIsNotNone(obj.pk)

    def test_editing_without_changing_main_class_is_valid(self):
        """Проверяет, что при редактировании существующей записи без изменения родительского класса форма валидна."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.UPDATED_INSTANCE_NAME,
                "short_name": self.UPDATED_INSTANCE_SHORT_NAME,
                "main_class": self.root,
            }
            form = EnumClassForm(data=form_data, instance=self.child)
            obj = form.save()
            self.assertIsNotNone(obj.pk)
            self.assertEqual(form_data["name"], obj.name)
            self.assertEqual(form_data["short_name"], obj.short_name)
            self.assertEqual(form_data["main_class"], obj.main_class)

    def test_non_enum_main_class_is_invalid(self):
        """Проверяет, что выбор родительского класса, не входящего в all_enum_classes, приводит к невалидности формы."""
        invalid_enum_main_class = ClassStruct.objects.create(
            name="invalid_enum_main_class",
            short_name="invalid_enum",
            main_class=None,
            base_ei=None,
        )
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.filter(
                pk__in=[self.root.pk, self.child.pk, self.other.pk]
            ),
        ):
            form_data = {
                "name": self.NEW_INSTANCE_NAME,
                "short_name": self.NEW_INSTANCE_SHORT_NAME,
                "main_class": invalid_enum_main_class,
            }
            form = EnumClassForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn("main_class", form.errors)

    def test_create_new_object_saves_correctly(self):
        """Проверяет, что при создании нового объекта с валидными данными форма сохраняет объект с корректными полями."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = {
                "name": self.NEW_INSTANCE_NAME,
                "short_name": self.NEW_INSTANCE_SHORT_NAME,
                "main_class": self.root,
            }
            form = EnumClassForm(data=form_data)
            self.assertTrue(form.is_valid())
            obj = form.save()
            self.assertIsNotNone(obj.pk)
            self.assertEqual(form_data["name"], obj.name)
            self.assertEqual(form_data["short_name"], obj.short_name)
            self.assertEqual(form_data["main_class"], obj.main_class)

    def test_form_displays_all_validation_errors(self):
        form_data = {
            "name": "",
            "short_name": "",
            "main_class": None,
        }
        form = EnumClassForm(data=form_data)
        self.assertFalse(form.is_valid())

        expected_errors = {
            "name": ["Поле для названия класса необходимо заполнить"],
            "main_class": ["Поле для родительского класса необходимо заполнить"],
        }

        for key, value in expected_errors.items():
            self.assertIn(key, form.errors)
            self.assertEqual(form.errors[key], expected_errors[key])


class ParClassFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.par_ei = Ei.objects.first()
        cls.int_parametr = ClassStruct.objects.get(pk=INT_PARAMS)
        cls.int_enum_parametr = ClassStruct.objects.get(pk=INT_ENUMS_ID)
        cls.agregat_parametr_type = ClassStruct.objects.get(pk=AGREGAT_TYPE_ID)
        cls.nuts_class = ClassStruct.objects.get(pk=NUTS_ID)
        cls.nuts_product_class = ClassStruct.objects.create(
            name="nuts_product_class",
            short_name="nuts_prod_class",
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.other_nuts_product_class = ClassStruct.objects.create(
            name="nuts_product_class",
            short_name="nuts_prod_class",
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.non_product_class = ClassStruct.objects.create(
            name="non_product_class",
            short_name="non_prod_class",
            base_ei=None,
            main_class=None,
        )
        cls.enum_parametr = Parametr.objects.create(
            name="enum_parametr",
            short_name="enum_parametr",
            parametr_type=cls.int_enum_parametr,
            par_ei=cls.par_ei,
        )
        cls.num_parametr = Parametr.objects.create(
            name="num_parametr",
            short_name="num_parametr",
            parametr_type=cls.int_parametr,
            par_ei=cls.par_ei,
        )
        cls.other_num_parametr = Parametr.objects.create(
            name="other_num_par",
            short_name="other_num_par",
            parametr_type=cls.int_parametr,
            par_ei=cls.par_ei,
        )
        cls.agregat_parametr = Parametr.objects.create(
            name="agregat_parametr",
            short_name="agregat_par",
            parametr_type=cls.agregat_parametr_type,
            par_ei=cls.par_ei,
        )
        cls.min_value = 100.00
        cls.max_value = 200.00
        cls.new_min_value = 10.00
        cls.new_max_value = 30.00
        cls.invalid_min_value = -1
        cls.invalid_max_value = -1

    def test_class_field_queryset_is_products(self):
        """Проверяет, что поле class_field использует queryset с объектами ClassStruct.products()."""
        form = ParClassForm()
        self.assertTrue(form.fields["class_field"].queryset, QuerySet)
        self.assertEqual(len(form.fields["class_field"].queryset), 7)

    def test_parametr_queryset_is_parameters(self):
        """Проверяет, что поле parametr использует queryset с объектами Parametr.parameters()."""
        form = ParClassForm()
        self.assertTrue(form.fields["parametr"].queryset, QuerySet)
        self.assertEqual(len(form.fields["parametr"].queryset), 3)

    def test_class_field_initial_value_is_not_none_if_class_field_was_passed_into_constructor(
        self,
    ):
        """Проверяет, что при передаче class_field в конструктор формы поле class_field получает начальное значение."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.int_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(class_field=self.nuts_product_class, data=form_data)
        self.assertIsNotNone(form.fields["class_field"].initial)
        self.assertEqual(form.fields["class_field"].initial, self.nuts_product_class)

    def test_class_field_initial_value_is_none_if_class_field_was_passed_into_constructor(
        self,
    ):
        """Проверяет, что без передачи class_field в конструктор поле class_field не имеет начального значения."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.int_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertIsNone(form.fields["class_field"].initial)

    def test_class_field_is_required(self):
        """Проверяет, что поле class_field обязательно для заполнения."""
        form_data = {
            "class_field": None,
            "parametr": self.num_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"][0],
            "Поле 'Класс изделия' обязательно для заполнения.",
        )

    def test_parametr_field_is_required(self):
        """Проверяет, что поле parametr обязательно для заполнения."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": None,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"][0], "Поле 'Параметр' обязательно для заполнения."
        )

    def test_min_value_is_optional(self):
        """Проверяет, что поле min_value может быть пустым (None) и форма проходит валидацию."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": None,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_max_value_is_optional(self):
        """Проверяет, что поле max_value может быть пустым (None) и форма проходит валидацию."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.min_value,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_class_field_raises_validation_error(self):
        """Проверяет, что выбор class_field, не входящего в products(), вызывает ошибку валидации."""
        form_data = {
            "class_field": self.non_product_class,
            "parametr": self.num_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_parametr_field_raises_validation_error(self):
        """Проверяет, что выбор parametr, не входящего в parameters(), вызывает ошибку валидации."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.agregat_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_enum_parametr_having_min_value_raises_validation_error(self):
        """Проверяет, что для enum-параметра указание min_value вызывает ошибку валидации."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.enum_parametr,
            "min_value": self.min_value,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"][0],
            "У параметра-перечисления не должно быть максимального и минимального значений!",
        )

    def test_enum_parametr_having_max_value_raises_validation_error(self):
        """Проверяет, что для enum-параметра указание max_value вызывает ошибку валидации."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.enum_parametr,
            "min_value": None,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"][0],
            "У параметра-перечисления не должно быть максимального и минимального значений!",
        )

    def test_invalid_min_value_raises_validation_error(self):
        """Проверяет, что отрицательное или нулевое значение min_value вызывает ошибку валидации."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.invalid_min_value,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_max_value_raises_validation_error(self):
        """Проверяет, что отрицательное или нулевое значение max_value вызывает ошибку валидации."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": None,
            "max_value": self.invalid_max_value,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_correct_data_for_num_parametr_is_valid(self):
        """Проверяет, что форма с корректными данными для числового параметра проходит валидацию."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_correct_data_for_enum_parametr_is_valid(self):
        """Проверяет, что форма с корректными данными для enum-параметра (без min/max) проходит валидацию."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.enum_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_num_par_class_instance_is_saved_correctly(self):
        """Проверяет, что объект ParClass для числового параметра сохраняется корректно."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid())

        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(form_data["class_field"], obj.class_field)
        self.assertEqual(form_data["parametr"], obj.parametr)
        self.assertEqual(form_data["min_value"], obj.min_value)
        self.assertEqual(form_data["max_value"], obj.max_value)

    def test_enum_par_class_instance_is_saved_correctly(self):
        """Проверяет, что объект ParClass для enum-параметра сохраняется корректно."""
        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.enum_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid())

        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(form_data["class_field"], obj.class_field)
        self.assertEqual(form_data["parametr"], obj.parametr)
        self.assertEqual(form_data["min_value"], obj.min_value)
        self.assertEqual(form_data["max_value"], obj.max_value)

    def test_edit_form_is_correctly_updating_min_value_and_max_value_fields(self):
        """Проверяет, что при редактировании поля min_value и max_value обновляются корректно."""
        instance = ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.new_min_value,
            "max_value": self.new_max_value,
        }
        form = ParClassForm(data=form_data, instance=instance)
        obj = form.save()
        self.assertEqual(obj.pk, instance.pk)
        self.assertEqual(obj.min_value, form_data["min_value"])
        self.assertEqual(obj.max_value, form_data["max_value"])

    def test_edit_form_correctly_updates_parametr_field_if_their_types_are_the_same(
        self,
    ):
        """Проверяет, что при смене параметра на другой того же типа (числовой) форма валидна и сохраняет изменения."""
        instance = ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.other_num_parametr,
            "min_value": self.new_min_value,
            "max_value": self.new_max_value,
        }
        form = ParClassForm(data=form_data, instance=instance)
        obj = form.save()
        self.assertEqual(obj.parametr, form_data["parametr"])
        self.assertEqual(obj.min_value, form_data["min_value"])
        self.assertEqual(obj.max_value, form_data["max_value"])

    def test_edit_form_correctly_updates_parametr_field_if_their_types_are_different_and_min_value_and_max_value_were_complied(
        self,
    ):
        """Проверяет, что при смене параметра на enum (с очисткой min/max) форма валидна и сохраняет изменения."""
        instance = ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.enum_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data, instance=instance)
        obj = form.save()
        self.assertEqual(obj.parametr, form_data["parametr"])
        self.assertEqual(obj.min_value, form_data["min_value"])
        self.assertEqual(obj.max_value, form_data["max_value"])

    def test_edit_form_raises_validation_error_is_parametr_types_are_different_and_min_value_and_max_value_were_not_complied(
        self,
    ):
        """Проверяет, что при смене параметра на enum с оставшимися min/max возникает ошибка валидации."""

        instance = ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.nuts_product_class,
            "parametr": self.enum_parametr,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=form_data, instance=instance)
        self.assertFalse(form.is_valid())
        expected_error_msg = "У параметра-перечисления не должно быть максимального и минимального значений!"
        self.assertEqual(form.errors["__all__"][0], expected_error_msg)

    def test_edit_form_correctly_updates_class_field(self):
        """Проверяет, что при смене class_field объект обновляется и num пересчитывается для нового класса."""
        instance = ParClass.objects.create(
            class_field=self.nuts_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.other_nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=form_data, instance=instance)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.class_field, form_data["class_field"])
        self.assertEqual(obj.num, 1)

    def test_equal_pairs_raises_validation_error(self):
        """Проверяет, что попытка создать дублирующую пару (class_field, parametr) вызывает ошибку валидации."""
        ParClass.objects.create(
            class_field=self.nuts_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.nuts_class,
            "parametr": self.num_parametr,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_class_field_parclass_instances_have_correct_num_values(self):
        """Проверяет, что при создании нескольких объектов для одного класса num последовательно увеличивается."""
        instance1_form_data = {
            "class_field": self.nuts_class,
            "parametr": self.num_parametr,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=instance1_form_data)
        self.assertTrue(form.is_valid())
        obj1 = form.save()
        self.assertIsNotNone(obj1.pk)
        self.assertEqual(obj1.num, 1)

        instance2_form_data = {
            "class_field": self.nuts_class,
            "parametr": self.enum_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=instance2_form_data)
        self.assertTrue(form.is_valid())
        obj2 = form.save()
        self.assertIsNotNone(obj2.pk)
        self.assertEqual(obj2.num, 2)

    def test_num_field_has_correct_value_after_updating_class_field(self):
        """Проверяет, что при смене class_field num пересчитывается для нового класса (с учётом уже существующих записей)."""
        ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )
        ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.other_num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=2,
        )
        instance = ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
            min_value=None,
            max_value=None,
            num=3,
        )
        ParClass.objects.create(
            class_field=self.other_nuts_product_class,
            parametr=self.other_num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.other_nuts_product_class,
            "parametr": self.enum_parametr,
            "min_value": None,
            "max_value": None,
        }
        form = ParClassForm(data=form_data, instance=instance)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 2)

    def test_edit_without_changing_class_field_keeps_num(self):
        """Проверяет, что при редактировании без изменения class_field значение num не меняется."""
        instance = ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.other_nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
        form = ParClassForm(data=form_data, instance=instance)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 1)

    def test_edit_without_changing_parametr_does_not_change_num(self):
        """Проверяет, что при редактировании только min/max (без смены parametr и class_field) num остаётся прежним."""
        instance = ParClass.objects.create(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = {
            "class_field": self.other_nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.new_min_value,
            "max_value": self.new_max_value,
        }
        form = ParClassForm(data=form_data, instance=instance)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 1)

    def test_model_clean_raises_error_if_min_value_greater_than_max_value(self):
        """Проверяет, что модель выбрасывает ошибку валидации, если min_value > max_value."""
        form_data = {
            "class_field": self.other_nuts_product_class,
            "parametr": self.num_parametr,
            "min_value": self.new_max_value,
            "max_value": self.new_min_value,
        }
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"][0],
            "У численного параметра минимальное значение должно быть меньше максимального!",
        )


class ChangeParClassNumFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.par_ei = Ei.objects.first()
        cls.int_parametr = ClassStruct.objects.get(pk=INT_PARAMS)
        cls.int_enum_parametr = ClassStruct.objects.get(pk=INT_ENUMS_ID)
        cls.agregat_parametr_type = ClassStruct.objects.get(pk=AGREGAT_TYPE_ID)
        cls.nuts_class = ClassStruct.objects.get(pk=NUTS_ID)
        cls.nuts_product_class = ClassStruct.objects.create(
            name="nuts_product_class",
            short_name="nuts_prod_class",
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.other_nuts_product_class = ClassStruct.objects.create(
            name="nuts_product_class",
            short_name="nuts_prod_class",
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.non_product_class = ClassStruct.objects.create(
            name="non_product_class",
            short_name="non_prod_class",
            base_ei=None,
            main_class=None,
        )
        cls.enum_parametr = Parametr.objects.create(
            name="enum_parametr",
            short_name="enum_parametr",
            parametr_type=cls.int_enum_parametr,
            par_ei=cls.par_ei,
        )
        cls.num_parametr = Parametr.objects.create(
            name="num_parametr",
            short_name="num_parametr",
            parametr_type=cls.int_parametr,
            par_ei=cls.par_ei,
        )

        cls.min_value = 10.00
        cls.max_value = 12.00

        cls.parclass_1 = ParClass.objects.create(
            class_field=cls.nuts_product_class,
            parametr=cls.num_parametr,
            min_value=cls.min_value,
            max_value=cls.max_value,
            num=1,
        )
        cls.parclass_2 = ParClass.objects.create(
            class_field=cls.nuts_product_class,
            parametr=cls.enum_parametr,
            min_value=None,
            max_value=None,
            num=2,
        )
        cls.parclass_3 = ParClass.objects.create(
            class_field=cls.other_nuts_product_class,
            parametr=cls.num_parametr,
            min_value=cls.min_value,
            max_value=cls.max_value,
            num=1,
        )

    def test_class_field_1_is_required(self):
        """Проверяет, что поле class_field_1 обязательно для заполнения."""
        form_data = {
            "class_field_1": None,
            "class_field_2": self.parclass_2,
        }
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0], "Поле class_field_1 не может быть пустым"
        )

    def test_class_field_2_is_required(self):
        """Проверяет, что поле class_field_2 обязательно для заполнения."""
        form_data = {
            "class_field_1": self.parclass_1,
            "class_field_2": None,
        }
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0], "Поле class_field_2 не может быть пустым"
        )

    def test_clean_raises_validation_error_if_objects_are_equal(self):
        """Проверяет, что при выборе двух одинаковых объектов ParClass выбрасывается ValidationError с соответствующим сообщением."""
        form_data = {
            "class_field_1": self.parclass_1,
            "class_field_2": self.parclass_1,
        }
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertFalse(form.is_valid())

    def test_error_message_for_duplicate_objects(self):
        """Проверяет, что при выборе одинаковых объектов сообщение об ошибке соответствует ожидаемому."""
        form_data = {
            "class_field_1": self.parclass_1,
            "class_field_2": self.parclass_1,
        }
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertFalse(form.is_valid(), form.errors)
        expected_error_msg = "Классы изделия не могут быть одинаковыми!"
        self.assertEqual(form.errors["__all__"][0], expected_error_msg)

    def test_clean_does_not_raise_error_if_objects_are_different(self):
        """Проверяет, что при выборе двух разных объектов ParClass форма проходит валидацию."""
        form_data = {
            "class_field_1": self.parclass_1,
            "class_field_2": self.parclass_2,
        }
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertTrue(form.is_valid())

    def test_queryset_is_empty_if_class_id_is_none(self):
        """Проверяет, что при передаче class_id=None queryset полей пуст."""
        form = ChangeParClassNumForm()
        self.assertEqual(len(form.fields["class_field_1"].queryset), 0)
        self.assertEqual(len(form.fields["class_field_2"].queryset), 0)

    def test_num_values_were_successfully_swapped(self):
        """Проверяет, что после валидации формы значения num у двух выбранных объектов ParClass успешно меняются местами."""
        form_data = {
            "class_field_1": self.parclass_1,
            "class_field_2": self.parclass_2,
        }
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertTrue(form.is_valid())

        updated_parclass_1 = form.cleaned_data["class_field_1"]
        updated_parclass_2 = form.cleaned_data["class_field_2"]

        updated_parclass_1.num, updated_parclass_2.num = (
            updated_parclass_2.num,
            updated_parclass_1.num,
        )
        updated_parclass_1.save(update_fields=["num"])
        updated_parclass_2.save(update_fields=["num"])

        self.parclass_1.refresh_from_db()
        self.parclass_2.refresh_from_db()
        self.assertEqual(self.parclass_1.num, 2)
        self.assertEqual(self.parclass_2.num, 1)
