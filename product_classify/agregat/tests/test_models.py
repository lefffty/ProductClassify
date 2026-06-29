from django.db import IntegrityError
from django.test import TestCase

from classes.models import ClassStruct
from products.constants import INT_PARAMS

from ..constants import AGREGAT_TYPE_ID
from ..models import Agregat, Parametr


class AgregatModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        parametr_type = ClassStruct.objects.get(pk=INT_PARAMS)
        agregat_type = ClassStruct.objects.get(pk=AGREGAT_TYPE_ID)

        cls.agr = Parametr.objects.create(
            name="test_agregat",
            short_name="test",
            parametr_type=parametr_type,
            par_ei=None,
        )
        cls.par = Parametr.objects.create(
            name="test_parametr",
            short_name="test",
            parametr_type=agregat_type,
            par_ei=None,
        )

    def test_create_with_minimal_requirements(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        agregat = Agregat.objects.create(
            agr=self.agr,
            par=self.par,
            num=num,
        )
        self.assertIsNotNone(agregat.pk)

    def test_string_representation(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        agregat = Agregat.objects.create(
            agr=self.agr,
            par=self.par,
            num=num,
        )
        expected_representation = "test_agregat - test_parametr"
        self.assertEqual(str(agregat), expected_representation)

    def test_agregat_relationship(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        agregat = Agregat.objects.create(
            agr=self.agr,
            par=self.par,
            num=num,
        )
        self.assertIn(agregat, self.agr.agregat_parametrs.all())

    def test_parametr_relationship(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        agregat = Agregat.objects.create(
            agr=self.agr,
            par=self.par,
            num=num,
        )
        self.assertIn(agregat, self.par.agregat_set.all())

    def test_unique_constraints(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        Agregat.objects.create(
            agr=self.agr,
            par=self.par,
            num=num,
        )
        with self.assertRaises(IntegrityError):
            num += 1
            Agregat.objects.create(
                agr=self.agr,
                par=self.par,
                num=num,
            )
