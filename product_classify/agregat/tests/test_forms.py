from django.test import TestCase
from django.db.models import QuerySet

from ei.models import Ei
from classes.models import ClassStruct
from parametr.models import Parametr
from products.constants import DOUBLE_PARAMS

from agregat.models import Agregat
from agregat.constants import AGREGAT_TYPE_ID
from agregat.forms import AgregatForm


class AgregatFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.par_ei = Ei.objects.first()
        cls.agregat_type = ClassStruct.objects.get(pk=AGREGAT_TYPE_ID)
        cls.double_parametr_type = ClassStruct.objects.get(pk=DOUBLE_PARAMS)

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
