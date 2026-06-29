from django.test import TestCase

from classes.models import ClassStruct
from products.constants import INT_PARAMS
from ei.models import Ei

from ..models import Parametr
from ..constants import AGREGAT_TYPE_ID


class ParametrModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.par_ei = Ei.objects.first()
        cls.parametr_type = ClassStruct.objects.get(pk=INT_PARAMS)
        cls.agregat_type = ClassStruct.objects.get(pk=AGREGAT_TYPE_ID)

    def test_create_with_minimum_requirements(self):
        parametr = Parametr.objects.create(
            name="test",
            parametr_type=self.parametr_type,
            par_ei=self.par_ei,
        )
        self.assertIsNotNone(parametr.pk)

    def test_string_representation_with_unit_of_measure(self):
        parametr = Parametr(
            name="test",
            parametr_type=self.parametr_type,
            par_ei=self.par_ei,
        )
        expected_representation = "test, м"
        self.assertEqual(str(parametr), expected_representation)

    def test_string_representation_without_unit_of_measure(self):
        parametr = Parametr(
            name="test",
            parametr_type=self.parametr_type,
        )
        expected_representation = "test"
        self.assertEqual(str(parametr), expected_representation)

    def test_parametr_type_relationship(self):
        parametr = Parametr.objects.create(
            name="test",
            parametr_type=self.parametr_type,
            par_ei=self.par_ei,
        )
        self.assertIn(parametr, self.parametr_type.type_parameters.all())

    def test_ei_relationship(self):
        parametr = Parametr.objects.create(
            name="test",
            parametr_type=self.parametr_type,
            par_ei=self.par_ei,
        )
        self.assertIn(parametr, self.par_ei.parametr_set.all())

    def test_get_parametrs(self):
        parametr = Parametr.objects.create(
            name="test",
            parametr_type=self.parametr_type,
            par_ei=self.par_ei,
        )
        parametrs = Parametr.parameters()
        self.assertEqual(parametrs.count(), 1)
        self.assertIn(parametr, parametrs)

    def test_get_agregats(self):
        agregat = Parametr.objects.create(
            name="test",
            parametr_type=self.agregat_type,
            par_ei=self.par_ei,
        )
        agregats = Parametr.agregats()
        self.assertEqual(agregats.count(), 1)
        self.assertIn(agregat, agregats)
