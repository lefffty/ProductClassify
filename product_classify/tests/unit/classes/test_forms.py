from django.db.models import QuerySet

from unittest.mock import patch

from tests.unit.base import BaseUnitTestCase
from tests.unit.ei.factories.ei import EiFactory
from tests.unit.parametr.factories.parametr import ParametrFactory
from tests.unit.classes.factories.parclass import (
    ParClassFormData,
    ParClassFactory,
    ChangeParClassFormData
)
from tests.unit.classes.factories.class_struct import (
    ClassFormData,
    ProdClassFormData,
    EnumsClassFormData,
    ClassStructFactory,
    ChildClassStructFactory,
)

from ei.models import Ei

from classes.constants import (
    ParamIds,
    EnumsIds,
    MetaConsts,
    ProductsConsts,
    OperationConsts,
)
from classes.errors import ClassStructErrors, ParClassErrors, ChangeParClassErrors
from classes.models import (
    ClassStruct,
    ParClass
)
from classes.forms import (
    EconomicActivitySubjectClassForm,
    MeansOfLaborClassForm,
    ParClassForm,
    ProdClassForm,
    EnumClassForm,
    OperationClassForm,
    ChangeParClassNumForm,
    ProfessionClassForm,
    QualificationClassForm,
)


class ProdClassFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()

        cls.parent = ClassStruct.objects.create(
            name="class",
            short_name="class",
            base_ei=None,
            main_class=ClassStruct.objects.get(pk=ProductsConsts.PRODUCT_ID),
        )
        cls.child = ClassStruct.objects.create(
            name="class",
            short_name="class",
            base_ei=None,
            main_class=cls.parent,
        )
        cls.grandchild = ClassStruct.objects.create(
            name="class",
            short_name="class",
            base_ei=None,
            main_class=cls.child,
        )
        
        cls.invalid_data_with_cycle_reference = ProdClassFormData(main_class=cls.child.pk)
        cls.invalid_data_with_cycle_self_reference = ProdClassFormData(main_class=cls.parent.pk)
        cls.invalid_data_with_cycle_transitive_reference = ProdClassFormData(main_class=cls.grandchild.pk)

        cls.root = ClassStructFactory(base_ei=cls.base_ei)
        cls.child = ChildClassStructFactory(base_ei=cls.base_ei, main_class=cls.root)
        cls.other = ClassStructFactory(base_ei=cls.base_ei)

        cls.invalid_main_class = ClassStructFactory(base_ei=cls.base_ei)
        cls.valid_main_class = ClassStructFactory(base_ei=cls.base_ei, main_class=cls.child)
        cls.ei = EiFactory()

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

    def test_name_field_is_required(self):
        """Проверяет, что поле name обязательно для заполнения и выводится кастомное сообщение об ошибке."""
        form_data = ProdClassFormData(name="", main_class=self.valid_main_class.pk, base_ei=self.base_ei.pk)
        form = ProdClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"][0],
            ClassStructErrors.EMPTY_NAME_ERROR
        )

    def test_main_class_field_is_required(self):
        """Проверяет, что поле main_class обязательно для заполнения и выводится кастомное сообщение об ошибке."""
        form_data = ProdClassFormData(main_class="", base_ei=self.ei.pk)
        form = ProdClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(
            form.errors["main_class"][0],
            ClassStructErrors.EMPTY_MAIN_CLASS_ERROR,
        )

    def test_non_terminal_main_class_is_invalid(self):
        """Проверяет, что выбор родительского класса, не входящего в терминальные классы, приводит к невалидности формы."""
        form_data = ProdClassFormData(main_class=self.invalid_main_class.pk, base_ei=self.base_ei.pk)
        form = ProdClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_clean_does_not_raise_error_when_no_cycle_while_editing_existing_record(
        self,
    ):
        """Проверяет, что при редактировании существующей записи без создания цикла форма валидна и объект сохраняется с новым родителем."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = ProdClassFormData(main_class=self.other.pk, base_ei=self.base_ei.pk)
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
            form_data = ProdClassFormData(main_class=self.root.pk, base_ei=self.ei.pk)
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
            form_data = ProdClassFormData(main_class=self.other.pk, base_ei=self.base_ei.pk)
            form = ProdClassForm(data=form_data, instance=self.root)
            self.assertTrue(form.is_valid())
            obj = form.save()
            self.assertEqual(obj.pk, self.root.pk)
            self.assertEqual(obj.name, form_data["name"])

    def test_cycle_not_checked_for_new_object(self):
        """Проверяет, что для новых объектов (без instance.pk) проверка циклов не выполняется."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            with patch.object(
                ClassStruct, "check_classificator_cycle"
            ) as mock_check_classificator_cycle:
                form_data = ProdClassFormData(main_class=self.root.pk, base_ei=self.base_ei.pk)
                form = ProdClassForm(data=form_data)
                self.assertTrue(form.is_valid())
                mock_check_classificator_cycle.assert_not_called()

    def test_short_name_is_optional(self):
        """Проверяет, что поле short_name необязательно (может быть None) и форма остаётся валидной."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = ProdClassFormData(short_name="", main_class=self.valid_main_class.pk, base_ei=self.ei.pk)
            form = ProdClassForm(data=form_data)
            self.assertTrue(form.is_valid())

    def test_base_ei_is_optional(self):
        """Проверяет, что поле base_ei необязательно (может быть None) и форма остаётся валидной."""
        with patch(
            "classes.models.ClassStruct.terminal_product_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = ProdClassFormData(main_class=self.valid_main_class.pk)
            form = ProdClassForm(data=form_data)
            self.assertTrue(form.is_valid())

    def test_form_displays_all_validation_errors(self):
        form_data = ProdClassFormData(name="", short_name="")
        form = ProdClassForm(data=form_data)
        self.assertFalse(form.is_valid())

        expected_errors = {
            "name": ClassStructErrors.EMPTY_NAME_ERROR,
            "main_class": ClassStructErrors.EMPTY_MAIN_CLASS_ERROR,
        }

        for key, _ in expected_errors.items():
            self.assertIn(key, form.errors)
            self.assertEqual(form.errors[key][0], expected_errors[key])

    def test_cycle_reference_causes_internal_error_exception_to_be_raised(self):
        form = ProdClassForm(self.invalid_data_with_cycle_reference, instance=self.parent)
        self.assertFalse(form.is_valid())
        self.assertIn(ProdClassForm.cycle_check_field, form.errors)
        self.assertEqual(
            form.errors[ProdClassForm.cycle_check_field],
            [ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR],
        )

    def test_cycle_self_reference_causes_internal_error_exception_to_be_raised(self):
        form = ProdClassForm(self.invalid_data_with_cycle_self_reference, instance=self.parent)
        self.assertFalse(form.is_valid())
        self.assertIn(ProdClassForm.cycle_check_field, form.errors)
        self.assertEqual(
            form.errors[ProdClassForm.cycle_check_field],
            [ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR],
        )

    def test_cycle_transitive_reference_causes_internal_error_exception_to_be_raised(self):
        form = ProdClassForm(self.invalid_data_with_cycle_transitive_reference, instance=self.parent)
        self.assertFalse(form.is_valid())
        self.assertIn(ProdClassForm.cycle_check_field, form.errors)
        self.assertEqual(
            form.errors[ProdClassForm.cycle_check_field],
            [ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR],
        )


class EnumClassFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_ei = Ei.objects.first()

        cls.string_enum = ClassStruct.objects.get(pk=EnumsIds.STRING)

        cls.parent_enum = ClassStruct.objects.create(
            name="class",
            short_name="class",
            main_class=cls.string_enum,
        )
        cls.child_enum = ClassStruct.objects.create(
            name="class",
            short_name="class",
            main_class=cls.parent_enum,
        )
        cls.grandchild_enum = ClassStruct.objects.create(
            name="class",
            short_name="class",
            main_class=cls.child_enum,
        )

        cls.invalid_data_with_cycle_reference = EnumsClassFormData(main_class=cls.child_enum.pk)
        cls.invalid_data_with_cycle_self_reference = EnumsClassFormData(main_class=cls.parent_enum.pk)
        cls.invalid_data_with_cycle_transitive_reference = EnumsClassFormData(main_class=cls.grandchild_enum.pk)

        cls.root = ClassStructFactory(base_ei=cls.base_ei)
        cls.child = ClassStructFactory(base_ei=cls.base_ei, main_class=cls.root)
        cls.other = ClassStructFactory(base_ei=cls.base_ei)

    def test_main_class_queryset_is_all_enum_classes(self):
        """Проверяет, что поле main_class в форме использует queryset из ClassStruct.all_enum_classes()."""
        form = EnumClassForm()
        self.assertIsInstance(form.fields["main_class"].queryset, QuerySet)

    def test_main_class_is_required(self):
        """Проверяет, что поле main_class обязательно для заполнения и выводится кастомное сообщение об ошибке."""
        form_data = EnumsClassFormData()
        form = EnumClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(
            form.errors["main_class"][0],
            ClassStructErrors.EMPTY_MAIN_CLASS_ERROR,
        )

    def test_name_is_required(self):
        """Проверяет, что поле name обязательно для заполнения и выводится кастомное сообщение об ошибке."""
        form_data = EnumsClassFormData(name="", main_class=self.other.pk)
        form = EnumClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"][0],
            ClassStructErrors.EMPTY_NAME_ERROR,
        )

    def test_short_name_is_optional(self):
        """Проверяет, что поле short_name может быть пустой строкой и форма остаётся валидной."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(short_name="", main_class=self.other.pk)
            form = EnumClassForm(data=form_data)
            self.assertTrue(form.is_valid(), form.errors)

    def test_short_name_accepts_none(self):
        """Проверяет, что поле short_name может быть None (пустое значение) и форма остаётся валидной."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(short_name="", main_class=self.other.pk)
            form = EnumClassForm(data=form_data)
            self.assertTrue(form.is_valid())

    def test_clean_raises_error_when_cycle_detected_while_editing_existing_record(self):
        """Проверяет, что при редактировании существующей записи и создании циклической ссылки форма невалидна и содержит ошибку о цикле."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(main_class=self.child.pk)
            form = EnumClassForm(data=form_data, instance=self.root)
            self.assertFalse(form.is_valid())
            self.assertIn("main_class", form.errors)
            self.assertEqual(
                form.errors["main_class"][0],
                ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR,
            )

    def test_clean_does_not_raise_error_when_no_cycle_while_editing_existing_record(
        self,
    ):
        """Проверяет, что при редактировании существующей записи без создания цикла форма валидна и объект сохраняется с новым родителем."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(main_class=self.other.pk)
            form = EnumClassForm(data=form_data, instance=self.root)
            self.assertTrue(form.is_valid())

    def test_clean_does_not_raise_error_when_no_cycle(self):
        """Проверяет, что при создании нового объекта без циклической ссылки форма валидна и объект сохраняется."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(main_class=self.root.pk)
            form = EnumClassForm(data=form_data)
            self.assertTrue(form.is_valid())

    def test_edit_existing_record_updates_object(self):
        """Проверяет, что при редактировании существующей записи форма обновляет поля объекта, а не создаёт новый."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(main_class=self.other.pk)
            form = EnumClassForm(data=form_data, instance=self.root)
            self.assertTrue(form.is_valid())
            obj = form.save()
            self.assertEqual(form_data["name"], obj.name)
            self.assertEqual(form_data["short_name"], obj.short_name)
            self.assertEqual(form_data["main_class"], obj.main_class.pk)

    def test_cycle_when_main_class_is_self(self):
        """Проверяет, что установка родительским классом самого себя приводит к ошибке цикла."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(main_class=self.root.pk)
            form = EnumClassForm(data=form_data, instance=self.root)
            self.assertFalse(form.is_valid())
            self.assertIn("main_class", form.errors)
            self.assertEqual(
                form.errors["main_class"][0],
                ClassStructErrors.CLASSIFICATOR_CYCLE_ERROR,
            )

    def test_cycle_not_checked_for_new_object(self):
        """Проверяет, что для новых объектов (без instance.pk) проверка циклов не выполняется."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            with patch.object(
                ClassStruct,
                "check_classificator_cycle",
            ) as mock_check_classificator_cycle:
                form_data = EnumsClassFormData(main_class=self.other.pk)
                form = EnumClassForm(data=form_data)
                self.assertTrue(form.is_valid())
                obj = form.save()
                mock_check_classificator_cycle.assert_not_called()
                self.assertIsNotNone(obj.pk)

    def test_editing_without_changing_main_class_is_valid(self):
        """Проверяет, что при редактировании существующей записи без изменения родительского класса форма валидна."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(main_class=self.root.pk)
            form = EnumClassForm(data=form_data, instance=self.child)
            obj = form.save()
            self.assertIsNotNone(obj.pk)
            self.assertEqual(form_data["name"], obj.name)
            self.assertEqual(form_data["short_name"], obj.short_name)
            self.assertEqual(form_data["main_class"], obj.main_class.pk)

    def test_non_enum_main_class_is_invalid(self):
        """Проверяет, что выбор родительского класса, не входящего в all_enum_classes, приводит к невалидности формы."""
        invalid_enum_main_class = ClassStructFactory()
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.filter(
                pk__in=[self.root.pk, self.child.pk, self.other.pk]
            ),
        ):
            form_data = EnumsClassFormData(main_class=invalid_enum_main_class.pk)
            form = EnumClassForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn("main_class", form.errors)

    def test_create_new_object_saves_correctly(self):
        """Проверяет, что при создании нового объекта с валидными данными форма сохраняет объект с корректными полями."""
        with patch(
            "classes.models.ClassStruct.all_enum_classes",
            return_value=ClassStruct.objects.all(),
        ):
            form_data = EnumsClassFormData(main_class=self.root.pk)
            form = EnumClassForm(data=form_data)
            self.assertTrue(form.is_valid())
            obj = form.save()
            self.assertIsNotNone(obj.pk)
            self.assertEqual(form_data["name"], obj.name)
            self.assertEqual(form_data["short_name"], obj.short_name)
            self.assertEqual(form_data["main_class"], obj.main_class.pk)

    def test_form_displays_all_validation_errors(self):
        form_data = EnumsClassFormData(name="", short_name="")
        form = EnumClassForm(data=form_data)
        self.assertFalse(form.is_valid())

        expected_errors = {
            "name": ["Поле для названия класса необходимо заполнить"],
            "main_class": ["Поле для родительского класса необходимо заполнить"],
        }

        for key, _ in expected_errors.items():
            self.assertIn(key, form.errors)
            self.assertEqual(form.errors[key], expected_errors[key])


class ParClassFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.par_ei = Ei.objects.first()
        cls.int_parametr = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.int_enum_parametr = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.agregat_parametr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_product_class = ClassStructFactory(main_class=cls.nuts_class)
        cls.other_nuts_product_class = ClassStructFactory(main_class=cls.nuts_class)
        cls.non_product_class = ClassStructFactory()
        cls.enum_parametr = ParametrFactory(parametr_type=cls.int_enum_parametr, par_ei=cls.par_ei)
        cls.num_parametr = ParametrFactory(parametr_type=cls.int_parametr, par_ei=cls.par_ei)
        cls.other_num_parametr = ParametrFactory(parametr_type=cls.int_parametr, par_ei=cls.par_ei)
        cls.agregat_parametr = ParametrFactory(parametr_type=cls.agregat_parametr_type, par_ei=cls.par_ei)
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
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.int_parametr,
            min_value=None,
            max_value=None,
            num=1,
        )
        form = ParClassForm(class_field=self.nuts_product_class, data=form_data)
        self.assertIsNotNone(form.fields["class_field"].initial)
        self.assertEqual(form.fields["class_field"].initial, self.nuts_product_class)

    def test_class_field_initial_value_is_none_if_class_field_was_passed_into_constructor(
        self,
    ):
        """Проверяет, что без передачи class_field в конструктор поле class_field не имеет начального значения."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.int_parametr,
            min_value="",
            max_value="",
            num=1,
        )
        form = ParClassForm(data=form_data)
        self.assertIsNone(form.fields["class_field"].initial)

    def test_class_field_is_required(self):
        """Проверяет, что поле class_field обязательно для заполнения."""
        form_data = ParClassFormData(
            class_field=None,
            parametr=self.num_parametr,
            min_value="",
            max_value="",
            num=1,
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["class_field"],
            ["Поле 'Класс изделия' обязательно для заполнения."],
        )

    def test_parametr_field_is_required(self):
        """Проверяет, что поле parametr обязательно для заполнения."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=None,
            min_value="",
            max_value="",
            num=1,
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["parametr"], ["Поле 'Параметр' обязательно для заполнения."]
        )

    def test_min_value_is_optional(self):
        """Проверяет, что поле min_value может быть пустым (None) и форма проходит валидацию."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value="",
        )
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_max_value_is_optional(self):
        """Проверяет, что поле max_value может быть пустым (None) и форма проходит валидацию."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            max_value="",
        )
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_class_field_raises_validation_error(self):
        """Проверяет, что выбор class_field, не входящего в products(), вызывает ошибку валидации."""
        form_data = ParClassFormData(
            class_field=self.non_product_class,
            parametr=self.num_parametr,
            min_value="",
            max_value="",
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_parametr_field_raises_validation_error(self):
        """Проверяет, что выбор parametr, не входящего в parameters(), вызывает ошибку валидации."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.agregat_parametr,
            min_value="",
            max_value="",
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_enum_parametr_having_min_value_raises_validation_error(self):
        """Проверяет, что для enum-параметра указание min_value вызывает ошибку валидации."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
            max_value="",
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"][0],
            ParClassErrors.ENUM_AGGREGATE_RANGE_ERROR.format(form_data["parametr"].name),
        )

    def test_enum_parametr_having_max_value_raises_validation_error(self):
        """Проверяет, что для enum-параметра указание max_value вызывает ошибку валидации."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
            min_value="",
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(
            form.errors["__all__"][0],
            ParClassErrors.ENUM_AGGREGATE_RANGE_ERROR.format(form_data["parametr"].name)
        )

    def test_invalid_min_value_raises_validation_error(self):
        """Проверяет, что отрицательное или нулевое значение min_value вызывает ошибку валидации."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.invalid_min_value,
            max_value="",
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_max_value_raises_validation_error(self):
        """Проверяет, что отрицательное или нулевое значение max_value вызывает ошибку валидации."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
            min_value="",
            max_value=self.invalid_max_value,
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_correct_data_for_num_parametr_is_valid(self):
        """Проверяет, что форма с корректными данными для числового параметра проходит валидацию."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
        )
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_correct_data_for_enum_parametr_is_valid(self):
        """Проверяет, что форма с корректными данными для enum-параметра (без min/max) проходит валидацию."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
            min_value="",
            max_value="",
        )
        form = ParClassForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_num_par_class_instance_is_saved_correctly(self):
        """Проверяет, что объект ParClass для числового параметра сохраняется корректно."""
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
        )
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
        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
            min_value=None,
            max_value=None,
        )
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
        instance = ParClassFactory(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            num=1,            
        )

        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,            
        )

        form = ParClassForm(data=form_data, instance=instance)
        obj = form.save()
        self.assertEqual(obj.pk, instance.pk)
        self.assertEqual(obj.min_value, form_data["min_value"])
        self.assertEqual(obj.max_value, form_data["max_value"])

    def test_edit_form_correctly_updates_parametr_field_if_their_types_are_the_same(
        self,
    ):
        """Проверяет, что при смене параметра на другой того же типа (числовой) форма валидна и сохраняет изменения."""
        instance = ParClassFactory(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            num=1,
        )

        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.other_num_parametr,
        )

        form = ParClassForm(data=form_data, instance=instance)
        obj = form.save()
        self.assertEqual(obj.parametr, form_data["parametr"])
        self.assertEqual(obj.min_value, form_data["min_value"])
        self.assertEqual(obj.max_value, form_data["max_value"])

    def test_edit_form_correctly_updates_parametr_field_if_their_types_are_different_and_min_value_and_max_value_were_complied(
        self,
    ):
        """Проверяет, что при смене параметра на enum (с очисткой min/max) форма валидна и сохраняет изменения."""
        instance = ParClassFactory(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            num=1,            
        )

        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
            min_value=None,
            max_value=None,
        )
        form = ParClassForm(data=form_data, instance=instance)
        obj = form.save()
        self.assertEqual(obj.parametr, form_data["parametr"])
        self.assertEqual(obj.min_value, form_data["min_value"])
        self.assertEqual(obj.max_value, form_data["max_value"])

    def test_edit_form_raises_validation_error_is_parametr_types_are_different_and_min_value_and_max_value_were_not_complied(
        self,
    ):
        """Проверяет, что при смене параметра на enum с оставшимися min/max возникает ошибка валидации."""

        instance = ParClassFactory(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            num=1,            
        )

        form_data = ParClassFormData(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
        )
        form = ParClassForm(data=form_data, instance=instance)
        self.assertFalse(form.is_valid())
        expected_error_msg = ParClassErrors.ENUM_AGGREGATE_RANGE_ERROR.format(form_data["parametr"].name)
        self.assertEqual(form.errors["__all__"][0], expected_error_msg)

    def test_edit_form_correctly_updates_class_field(self):
        """Проверяет, что при смене class_field объект обновляется и num пересчитывается для нового класса."""
        instance = ParClassFactory(
            class_field=self.nuts_class,
            parametr=self.num_parametr,
            num=1,            
        )

        form_data = ParClassFormData(
            class_field=self.other_nuts_product_class,
            parametr=self.num_parametr,
        )
        form = ParClassForm(data=form_data, instance=instance)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.class_field, form_data["class_field"])
        self.assertEqual(obj.num, 1)

    def test_equal_pairs_raises_validation_error(self):
        """Проверяет, что попытка создать дублирующую пару (class_field, parametr) вызывает ошибку валидации."""
        _ = ParClassFactory(
            class_field=self.nuts_class,
            parametr=self.num_parametr,
            num=1,
        )

        form_data = ParClassFormData(
            class_field=self.nuts_class,
            parametr=self.num_parametr,
            min_value=None,
            max_value=None,
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_class_field_parclass_instances_have_correct_num_values(self):
        """Проверяет, что при создании нескольких объектов для одного класса num последовательно увеличивается."""
        instance1_form_data = ParClassFormData(
            class_field=self.nuts_class,
            parametr=self.num_parametr,
        )
        form = ParClassForm(data=instance1_form_data)
        self.assertTrue(form.is_valid())
        obj1 = form.save()
        self.assertIsNotNone(obj1.pk)
        self.assertEqual(obj1.num, 1)

        instance2_form_data = ParClassFormData(
            class_field=self.nuts_class,
            parametr=self.enum_parametr,
            min_value=None,
            max_value=None,
        )
        form = ParClassForm(data=instance2_form_data)
        self.assertTrue(form.is_valid())
        obj2 = form.save()
        self.assertIsNotNone(obj2.pk)
        self.assertEqual(obj2.num, 2)

    def test_num_field_has_correct_value_after_updating_class_field(self):
        """Проверяет, что при смене class_field num пересчитывается для нового класса (с учётом уже существующих записей)."""
        ParClassFactory(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,            
        )
        ParClassFactory(
            class_field=self.nuts_product_class,
            parametr=self.other_num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=2,            
        )
        instance = ParClassFactory(
            class_field=self.nuts_product_class,
            parametr=self.enum_parametr,
            min_value=None,
            max_value=None,
            num=3,
        )
        ParClassFactory(
            class_field=self.other_nuts_product_class,
            parametr=self.other_num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,
        )

        form_data = ParClassFormData(
            class_field=self.other_nuts_product_class,
            parametr=self.enum_parametr,
            min_value=None,
            max_value=None,
        )
        form = ParClassForm(data=form_data, instance=instance)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 2)

    def test_edit_without_changing_class_field_keeps_num(self):
        """Проверяет, что при редактировании без изменения class_field значение num не меняется."""
        instance = ParClassFactory(
            class_field=self.nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.min_value,
            max_value=self.max_value,
            num=1,            
        )

        form_data = ParClassFormData(
            class_field=self.other_nuts_product_class,
            parametr=self.num_parametr,
        )
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

        form_data = ParClassFormData(
            class_field=self.other_nuts_product_class,
            parametr=self.num_parametr,
        )
        form = ParClassForm(data=form_data, instance=instance)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 1)

    def test_model_clean_raises_error_if_min_value_greater_than_max_value(self):
        """Проверяет, что модель выбрасывает ошибку валидации, если min_value > max_value."""
        form_data = ParClassFormData(
            class_field=self.other_nuts_product_class,
            parametr=self.num_parametr,
            min_value=self.max_value,
            max_value=self.min_value,
        )
        form = ParClassForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["min_value"][0],
            "У численного параметра минимальное значение должно быть меньше максимального!",
        )


class ChangeParClassNumFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.par_ei = Ei.objects.first()
        cls.int_parametr = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.int_enum_parametr = ClassStruct.objects.get(pk=EnumsIds.INT)
        cls.agregat_parametr_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_product_class = ClassStructFactory(main_class=cls.nuts_class)
        cls.other_nuts_product_class = ClassStructFactory(main_class=cls.nuts_class)
        cls.non_product_class = ClassStructFactory()
        cls.enum_parametr = ParametrFactory(parametr_type=cls.int_enum_parametr, par_ei=cls.par_ei)
        cls.num_parametr = ParametrFactory(parametr_type=cls.int_parametr, par_ei=cls.par_ei)

        cls.parclass_1 = ParClassFactory(class_field=cls.nuts_product_class, parametr=cls.num_parametr, num=1)
        cls.parclass_2 = ParClassFactory(class_field=cls.nuts_product_class, parametr=cls.enum_parametr, num=2, min_value=None, max_value=None)
        cls.parclass_3 = ParClassFactory(class_field=cls.other_nuts_product_class, parametr=cls.num_parametr, num=1)

    def test_class_field_1_is_required(self):
        """Проверяет, что поле cls_1 обязательно для заполнения."""
        form_data = ChangeParClassFormData(
            cls_1=None,
            cls_2=self.parclass_2,
        )
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["cls_1"], ["Поле cls_1 не может быть пустым"]
        )

    def test_cls_2_is_required(self):
        """Проверяет, что поле cls_2 обязательно для заполнения."""
        form_data = ChangeParClassFormData(
            cls_1=self.parclass_1,
            cls_2=None,
        )
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["cls_2"], ["Поле cls_2 не может быть пустым"]
        )

    def test_clean_raises_validation_error_if_objects_are_equal(self):
        """Проверяет, что при выборе двух одинаковых объектов ParClass
        выбрасывается ValidationError с соответствующим сообщением."""
        form_data = ChangeParClassFormData(
            cls_1=self.parclass_1,
            cls_2=self.parclass_1,
        )
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertFalse(form.is_valid())

    def test_error_message_for_duplicate_objects(self):
        """Проверяет, что при выборе одинаковых объектов сообщение
        об ошибке соответствует ожидаемому."""
        form_data = ChangeParClassFormData(
            cls_1=self.parclass_1,
            cls_2=self.parclass_1,
        )
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(form.errors["__all__"][0], ChangeParClassErrors.EQUAL_PAR)

    def test_clean_does_not_raise_error_if_objects_are_different(self):
        """Проверяет, что при выборе двух разных объектов ParClass
        форма проходит валидацию."""
        form_data = ChangeParClassFormData(
            cls_1=self.parclass_1.pk,
            cls_2=self.parclass_2.pk,
        )
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertTrue(form.is_valid())

    def test_queryset_is_empty_if_class_id_is_none(self):
        """Проверяет, что при передаче class_id=None queryset полей пуст."""
        form = ChangeParClassNumForm()
        self.assertEqual(len(form.fields["cls_1"].queryset), 0)
        self.assertEqual(len(form.fields["cls_2"].queryset), 0)

    def test_num_values_were_successfully_swapped(self):
        """Проверяет, что после валидации формы значения num
        у двух выбранных объектов ParClass успешно меняются местами."""
        form_data = ChangeParClassFormData(
            cls_1=self.parclass_1.pk,
            cls_2=self.parclass_2.pk,
        )
        form = ChangeParClassNumForm(
            data=form_data, class_id=self.nuts_product_class.pk
        )
        self.assertTrue(form.is_valid())

        self.parclass_1.refresh_from_db()
        self.parclass_2.refresh_from_db()
        self.assertEqual(self.parclass_1.num, 2)
        self.assertEqual(self.parclass_2.num, 1)


class OperationClassFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.welding = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.non_operation = ClassStruct.objects.first()

        cls.valid_data = ClassFormData(main_class=cls.welding)
        cls.empty_name_data = ClassFormData(name="", main_class=cls.welding)
        cls.empty_main_class_data = ClassFormData()
        cls.empty_short_name_data = ClassFormData(short_name="", main_class=cls.welding)
        cls.non_operation_data = ClassFormData(main_class=cls.non_operation)

    def test_main_class_queryset_is_operations_queryset(self):
        form = OperationClassForm()
        self.assertIsInstance(form.fields["main_class"].queryset, QuerySet)
        self.assertEqual(len(form.fields["main_class"].queryset), len(ClassStruct.operations()))

    def test_name_field_is_required(self):
        form = OperationClassForm(self.empty_name_data)
        self.assertFalse(form.is_valid())

    def test_main_class_field_is_required(self):
        form = OperationClassForm(self.empty_main_class_data)
        self.assertFalse(form.is_valid())

    def test_short_name_field_is_optional(self):
        form = OperationClassForm(self.empty_short_name_data)
        self.assertTrue(form.is_valid())

    def test_non_operation_main_class_raises_validation_error(self):
        form = OperationClassForm(self.non_operation_data)
        self.assertFalse(form.is_valid())

    def test_operation_was_saved_successfully(self):
        form = OperationClassForm(self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertIsNotNone(instance.pk)
        self.assertEqual(instance.name, self.valid_data["name"])
        self.assertEqual(instance.short_name, self.valid_data["short_name"])
        self.assertEqual(instance.main_class, self.valid_data["main_class"])


class EconomicActivitySubjectClassFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.economic_activity_subject = ClassStruct.objects.get(
            pk=MetaConsts.ECONOMIC_ACTIVITY_SUBJECT
        )

        cls.invalid_main_class = (
            ClassStruct.objects
            .exclude(pk=MetaConsts.ECONOMIC_ACTIVITY_SUBJECT)
            .first()
        )

        cls.valid_data = ClassFormData(main_class=cls.economic_activity_subject)
        cls.empty_name_data = ClassFormData(name="", main_class=cls.economic_activity_subject)
        cls.empty_main_class_data = ClassFormData()
        cls.empty_short_name_data = ClassFormData(short_name="", main_class=cls.economic_activity_subject)
        cls.invalid_main_class_data = ClassFormData(main_class=cls.invalid_main_class)

    def test_valid_form(self):
        form = EconomicActivitySubjectClassForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_empty_name(self):
        form = EconomicActivitySubjectClassForm(data=self.empty_name_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"][0],
            ClassStructErrors.EMPTY_NAME_ERROR,
        )

    def test_empty_short_name(self):
        form = EconomicActivitySubjectClassForm(data=self.empty_short_name_data)
        self.assertTrue(form.is_valid())

    def test_empty_main_class(self):
        form = EconomicActivitySubjectClassForm(data=self.empty_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(
            form.errors["main_class"][0],
            ClassStructErrors.EMPTY_MAIN_CLASS_ERROR,
        )

    def test_invalid_main_class(self):
        form = EconomicActivitySubjectClassForm(data=self.invalid_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)


class MeansOfLaborClassFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_main_class = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.invalid_main_class = ClassStruct.objects.first()

        cls.valid_data = ClassFormData(main_class=cls.valid_main_class)
        cls.empty_name_data = ClassFormData(name="", main_class=cls.valid_main_class)
        cls.empty_main_class_data = ClassFormData()
        cls.invalid_main_class_data = ClassFormData(main_class=cls.invalid_main_class)

    def test_valid_form(self):
        form = MeansOfLaborClassForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_empty_name(self):
        form = MeansOfLaborClassForm(data=self.empty_name_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"][0],
            ClassStructErrors.EMPTY_NAME_ERROR,
        )

    def test_empty_main_class(self):
        form = MeansOfLaborClassForm(data=self.empty_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(
            form.errors["main_class"][0],
            ClassStructErrors.EMPTY_MAIN_CLASS_ERROR,
        )

    def test_invalid_main_class(self):
        form = MeansOfLaborClassForm(data=self.invalid_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)


class QualificationClassFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.qualification = ClassStruct.objects.get(pk=MetaConsts.QUALIFICATION)
        cls.invalid_main_class = (
            ClassStruct.objects
            .exclude(pk=MetaConsts.QUALIFICATION)
            .first()
        )
        cls.valid_data = ClassFormData(main_class=cls.qualification)
        cls.empty_name_data = ClassFormData(name="", main_class=cls.qualification)
        cls.empty_main_class_data = ClassFormData()
        cls.invalid_main_class_data = ClassFormData(main_class=cls.invalid_main_class)

    def test_valid_form(self):
        form = QualificationClassForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_empty_name(self):
        form = QualificationClassForm(data=self.empty_name_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"][0],
            ClassStructErrors.EMPTY_NAME_ERROR,
        )

    def test_empty_main_class(self):
        form = QualificationClassForm(data=self.empty_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(
            form.errors["main_class"][0],
            ClassStructErrors.EMPTY_MAIN_CLASS_ERROR,
        )

    def test_invalid_main_class(self):
        form = QualificationClassForm(data=self.invalid_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)

    def test_main_class_queryset_contains_only_qualification(self):
        form = QualificationClassForm()
        self.assertEqual(
            list(form.fields["main_class"].queryset.values_list("pk", flat=True)),
            [MetaConsts.QUALIFICATION],
        )


class ProfessionClassFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.profession = ClassStruct.objects.get(pk=MetaConsts.PROFESSION)

        cls.invalid_main_class = (
            ClassStruct.objects
            .exclude(pk=MetaConsts.PROFESSION)
            .first()
        )

        cls.valid_data = ClassFormData(main_class=cls.profession)
        cls.empty_name_data = ClassFormData(name="", main_class=cls.profession)
        cls.empty_main_class_data = ClassFormData()
        cls.invalid_main_class_data = ClassFormData(main_class=cls.invalid_main_class)

    def test_valid_form(self):
        form = ProfessionClassForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_empty_name(self):
        form = ProfessionClassForm(data=self.empty_name_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(
            form.errors["name"][0],
            ClassStructErrors.EMPTY_NAME_ERROR,
        )

    def test_empty_main_class(self):
        form = ProfessionClassForm(data=self.empty_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
        self.assertEqual(
            form.errors["main_class"][0],
            ClassStructErrors.EMPTY_MAIN_CLASS_ERROR,
        )

    def test_invalid_main_class(self):
        form = ProfessionClassForm(data=self.invalid_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertIn("main_class", form.errors)
