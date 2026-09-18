from django.db import IntegrityError

from tests.unit.base import BaseUnitTestCase
from tests.unit.agregat.factories.agregat import AgregatFactory
from tests.unit.parametr.factories.parametr import ParametrFactory

from classes.models import ClassStruct
from classes.constants import ParamIds

from agregat.models import Agregat


class AgregatModelTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        parametr_type = ClassStruct.objects.get(pk=ParamIds.INT)
        agregat_type = ClassStruct.objects.get(pk=ParamIds.AGREGAT)

        cls.agr = ParametrFactory(parametr_type=parametr_type)
        cls.par = ParametrFactory(parametr_type=agregat_type)

    def test_create_with_minimal_requirements(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        agregat = AgregatFactory(par=self.par, agr=self.agr, num=num)
        self.assertIsNotNone(agregat.pk)

    def test_string_representation(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        agregat = AgregatFactory(agr=self.agr, par=self.par, num=num)
        self.assertIsNotNone(str(agregat))

    def test_agregat_relationship(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        agregat = AgregatFactory(agr=self.agr, par=self.par, num=num)
        self.assertIn(agregat, self.agr.agregat_parametrs.all())

    def test_parametr_relationship(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        agregat = AgregatFactory(agr=self.agr, par=self.par, num=num)
        self.assertIn(agregat, self.par.agregat_set.all())

    def test_unique_constraints(self):
        num = Agregat.objects.filter(agr=self.agr).count() + 1
        AgregatFactory(agr=self.agr, par=self.par, num=num)
        with self.assertRaises(IntegrityError):
            num += 1
            AgregatFactory(agr=self.agr, par=self.par, num=num)
