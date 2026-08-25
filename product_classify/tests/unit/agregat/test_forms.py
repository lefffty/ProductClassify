from django.db.models import QuerySet

from tests.unit.base import BaseUnitTestCase

from ei.models import Ei
from classes.models import ClassStruct
from classes.constants import ParamIds
from parametr.models import Parametr
from agregat.models import Agregat
from agregat.forms import AgregatForm, ChangeAgregatNumForm


class AgregatFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.par_ei = Ei.objects.first()
        cls.agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.double_parametr_type = ClassStruct.objects.get(pk=ParamIds.DOUBLE)

        cls.agregat = Parametr.objects.create(
            name="Габариты",
            short_name="",
            par_ei=None,
            parametr_type=cls.agregat_type,
        )
        cls.par1 = Parametr.objects.create(
            name="Ширина",
            short_name="Ш",
            parametr_type=cls.double_parametr_type,
            par_ei=cls.par_ei,
        )
        cls.par2 = Parametr.objects.create(
            name="Длина",
            short_name="Дл",
            parametr_type=cls.double_parametr_type,
            par_ei=cls.par_ei,
        )

    def test_agr_field_queryset_is_agregats(self):
        """Проверяет, что поле agr использует queryset с объектами Parametr.agregats()."""
        form = AgregatForm()
        self.assertIsInstance(form.fields["agr"].queryset, QuerySet)
        self.assertEqual(len(form.fields["agr"].queryset), 1)

    def test_par_field_queryset_is_parameters(self):
        """Проверяет, что поле par использует queryset с объектами Parametr.parameters()."""
        form = AgregatForm()
        self.assertIsInstance(form.fields["par"].queryset, QuerySet)
        self.assertEqual(len(form.fields["par"].queryset), 2)

    def test_initial_par_field_is_none_if_agregat_was_not_passed_as_an_argument(self):
        """Проверяет, что при создании формы без передачи agr поле agr не имеет начального значения."""
        form = AgregatForm()
        self.assertIsNone(form.fields["agr"].initial)

    def test_initial_par_field_is_not_none_if_agregat_was_passed_as_an_argument(self):
        """Проверяет, что при передаче agr в конструктор формы поле agr получает начальное значение."""
        form = AgregatForm(agr=self.agregat)
        self.assertIsNotNone(form.fields["agr"].initial)

    def test_agr_field_is_required(self):
        """Проверяет, что поле agr обязательно для заполнения."""
        form_data = {
            "par": self.par1,
        }
        form = AgregatForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_par_field_is_required(self):
        """Проверяет, что поле par обязательно для заполнения."""
        form_data = {
            "par": None,
        }
        form = AgregatForm(data=form_data, agr=self.agregat)
        self.assertFalse(form.is_valid())

    def test_non_agregat_object_is_not_valid_for_agr_field(self):
        """Проверяет, что в поле agr нельзя выбрать объект, не являющийся агрегатом (тип 'Агрегат')."""
        form_data = {
            "par": self.par1,
        }
        form = AgregatForm(data=form_data, agr=self.par1)
        self.assertFalse(form.is_valid())

    def test_non_parameter_object_is_not_valid_for_par_field(self):
        """Проверяет, что в поле par нельзя выбрать объект, не являющийся параметром."""
        form_data = {
            "par": self.agregat,
        }
        form = AgregatForm(data=form_data, agr=self.agregat)
        self.assertFalse(form.is_valid())

    def test_standard_form_data_is_valid(self):
        """Проверяет, что форма с корректными данными (агрегат и параметр) проходит валидацию."""
        form_data = {
            "agr": self.agregat,
            "par": self.par1,
        }
        form = AgregatForm(data=form_data, agr=self.agregat)
        self.assertTrue(form.is_valid(), form.errors)

    def test_num_field_is_calculated_correctly_for_one_pair(self):
        """Проверяет, что при создании первой пары агрегат-параметр num становится равен 1."""
        form_data = {
            "agr": self.agregat,
            "par": self.par1,
        }
        form = AgregatForm(data=form_data, agr=self.agregat)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["num"], 1)

    def test_agregat_is_saved_correctly(self):
        """Проверяет, что объект Agregat сохраняется с корректными полями и num."""
        form_data = {
            "agr": self.agregat,
            "par": self.par1,
        }
        form = AgregatForm(data=form_data, agr=self.agregat)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.agr, form.cleaned_data["agr"])
        self.assertEqual(obj.par, form.cleaned_data["par"])
        self.assertEqual(obj.num, 1)

    def test_num_field_is_calculated_correctly_for_several_pairs(self):
        """Проверяет, что при добавлении нескольких пар num последовательно увеличивается (1, 2, ...)."""
        form_data = {
            "agr": self.agregat,
            "par": self.par1,
        }
        form = AgregatForm(data=form_data, agr=self.agregat)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.agr, form.cleaned_data["agr"])
        self.assertEqual(obj.par, form.cleaned_data["par"])
        self.assertEqual(obj.num, 1)

        form_data = {
            "agr": self.agregat,
            "par": self.par2,
        }
        form = AgregatForm(data=form_data, agr=self.agregat)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.agr, form.cleaned_data["agr"])
        self.assertEqual(obj.par, form.cleaned_data["par"])
        self.assertEqual(obj.num, 2)

    def test_unique_together_constraint_prevents_duplicate(self):
        """Проверяет, что попытка создать дублирующую пару (agr, par) вызывает ошибку валидации или IntegrityError."""
        Agregat.objects.create(
            agr=self.agregat,
            par=self.par1,
            num=1,
        )
        form_data = {
            "agr": self.agregat,
            "par": self.par1,
        }
        form = AgregatForm(data=form_data, agr=self.agregat)
        self.assertFalse(form.is_valid())

    def test_edit_par_does_not_change_num(self):
        """Проверяет, что при редактировании пары (изменении par) num остаётся прежним."""
        instance = Agregat.objects.create(
            agr=self.agregat,
            par=self.par1,
            num=1,
        )
        form_data = {
            "agr": self.agregat,
            "par": self.par2,
        }
        form = AgregatForm(data=form_data, agr=self.agregat, instance=instance)
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.num, 1)


class ChangeAgregatNumFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.par_ei = Ei.objects.first()
        cls.agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)
        cls.double_parametr_type = ClassStruct.objects.get(pk=ParamIds.DOUBLE)

        cls.agregat = Parametr.objects.create(
            name="Габариты",
            short_name="",
            par_ei=None,
            parametr_type=cls.agregat_type,
        )
        cls.other_agregat = Parametr.objects.create(
            name="Другой агрегат",
            short_name="",
            par_ei=None,
            parametr_type=cls.agregat_type,
        )
        cls.par1 = Parametr.objects.create(
            name="Ширина",
            short_name="Ш",
            parametr_type=cls.double_parametr_type,
            par_ei=cls.par_ei,
        )
        cls.par2 = Parametr.objects.create(
            name="Длина",
            short_name="Дл",
            parametr_type=cls.double_parametr_type,
            par_ei=cls.par_ei,
        )
        cls.other_agregat_par = Parametr.objects.create(
            name="Test parametr",
            short_name="Test parametr",
            parametr_type=cls.double_parametr_type,
            par_ei=cls.par_ei,
        )
        cls.invalid_par = Parametr.objects.create(
            name="Test parametr",
            short_name="Test parametr",
            parametr_type=cls.double_parametr_type,
            par_ei=cls.par_ei,
        )

        cls.agr_pair1 = Agregat.objects.create(
            agr=cls.agregat,
            par=cls.par1,
            num=1,
        )
        cls.agr_pair2 = Agregat.objects.create(
            agr=cls.agregat,
            par=cls.par2,
            num=2,
        )
        cls.agr_pair3 = Agregat.objects.create(
            agr=cls.other_agregat,
            par=cls.other_agregat_par,
            num=1,
        )

    def test_agr_param_1_queryset_is_related_to_given_agregat(self):
        """Проверяет, что поле par_1 содержит только записи Agregat, относящиеся к переданному агрегату."""
        form_data = {
            "par_1": self.agr_pair1,
            "par_2": self.agr_pair2,
        }
        form = ChangeAgregatNumForm(agr=self.agregat)
        self.assertIn(
            form_data["par_1"].par.pk,
            form.fields["par_1"].queryset.values_list("par__pk", flat=True),
        )

    def test_agr_param_2_queryset_is_related_to_given_agregat(self):
        """Проверяет, что поле par_2 содержит только записи Agregat, относящиеся к переданному агрегату."""
        form_data = {
            "par_1": self.agr_pair1,
            "par_2": self.agr_pair2,
        }
        form = ChangeAgregatNumForm(agr=self.agregat)
        self.assertIn(
            form_data["par_2"].par.pk,
            form.fields["par_2"].queryset.values_list("par__pk", flat=True),
        )

    def test_agr_param_queryset_empty_if_agr_is_none(self):
        """Проверяет, что при передаче agr=None queryset полей пуст."""
        form = ChangeAgregatNumForm(agr=None)
        self.assertFalse(form.fields["par_1"].queryset.exists())
        self.assertFalse(form.fields["par_2"].queryset.exists())

    def test_agr_param_1_field_is_required(self):
        """Проверяет, что поле par_1 обязательно для заполнения."""
        form_data = {
            "par_1": None,
            "par_2": self.agr_pair2,
        }
        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)
        self.assertFalse(form.is_valid())

    def test_agr_param_2_field_is_required(self):
        """Проверяет, что поле par_2 обязательно для заполнения."""
        form_data = {
            "par_1": self.agr_pair1,
            "par_2": None,
        }
        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)
        self.assertFalse(form.is_valid())

    def test_non_related_to_given_agregat_agr_param_1_is_invalid(self):
        """Проверяет, что выбор объекта Agregat, не связанного с переданным агрегатом, вызывает ошибку валидации."""
        form_data = {
            "par_1": self.invalid_par,
            "par_2": self.agr_pair2,
        }
        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)
        self.assertFalse(form.is_valid())

    def test_non_related_to_given_agregat_agr_param_2_is_invalid(self):
        """Проверяет, что выбор объекта Agregat, не связанного с переданным агрегатом, вызывает ошибку валидации."""
        form_data = {
            "par_1": self.agr_pair1,
            "par_2": self.invalid_par,
        }
        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)
        self.assertFalse(form.is_valid())

    def test_standard_form_data_is_valid(self):
        """Проверяет, что форма с двумя корректными записями Agregat из одного агрегата проходит валидацию."""
        form_data = {
            "par_1": self.agr_pair1,
            "par_2": self.agr_pair2,
        }
        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)
        self.assertTrue(form.is_valid())

    def test_equal_pairs_raises_validation_error(self):
        """Проверяет, что выбор двух одинаковых записей Agregat вызывает ошибку валидации."""
        form_data = {
            "par_1": self.agr_pair1,
            "par_2": self.agr_pair1,
        }
        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)
        self.assertFalse(form.is_valid())

    def test_num_values_are_changed_after_saving_form(self):
        """Проверяет, что после валидации формы значения num в выбранных записях меняются местами в БД."""
        form_data = {
            "par_1": self.agr_pair1,
            "par_2": self.agr_pair2,
        }
        self.assertEqual(self.agr_pair1.num, 1)
        self.assertEqual(self.agr_pair2.num, 2)

        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)
        self.assertTrue(form.is_valid())

        self.agr_pair1.refresh_from_db()
        self.agr_pair2.refresh_from_db()

        self.assertEqual(self.agr_pair1.num, 2)
        self.assertEqual(self.agr_pair2.num, 1)

    def test_clean_raises_error_if_param_from_different_agregat(self):
        """Проверяет, что выбор записи, принадлежащей другому агрегату, вызывает ошибку валидации (проверка queryset)."""
        form_data = {
            "par_1": self.agr_pair3,
            "par_2": self.agr_pair2,
        }
        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("par_1", form.errors)

    def test_form_does_not_save_objects_if_invalid(self):
        """Проверяет, что при невалидной форме изменения в БД не сохраняются."""
        original_num1 = self.agr_pair1.num
        original_num2 = self.agr_pair2.num
        form_data = {
            "par_1": self.agr_pair1,
            "par_2": self.agr_pair1,
        }
        form = ChangeAgregatNumForm(agr=self.agregat, data=form_data)
        self.assertFalse(form.is_valid())
        self.agr_pair1.refresh_from_db()
        self.agr_pair2.refresh_from_db()
        self.assertEqual(self.agr_pair1.num, original_num1)
        self.assertEqual(self.agr_pair2.num, original_num2)
