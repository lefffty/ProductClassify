from django.db import IntegrityError
from django.core.exceptions import ValidationError

from classes.models import ClassStruct
from classes.constants import (
    MetaConsts,
    OperationConsts,
    ProductsConsts,
    ProfessionConsts,
    QualificationConsts,
)
from tests.unit.classes.factories.class_struct import ClassStructFactory
from tests.unit.products.factories.product import ProdFactory
from tests.unit.route_tech.factories.eas import EASFactory
from tests.unit.route_tech.factories.gwc import GWCFactory
from tests.unit.route_tech.factories.prod_oper import ProdOperationFactory
from tests.unit.route_tech.factories.prod_oper_pos import ProdOperationPosFactory

from route_tech.models import (
    EconomicActivitySubject,
    GroupWorkingCenter,
    ProdOperation,
    ProdOperationPos
)
from route_tech.constants import ProdOperConsts, ProdOperationPosConsts

from tests.unit.base import BaseUnitTestCase


class EconomicActivityEntityTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.workshop = ClassStruct.objects.get(pk=MetaConsts.WORKSHOP)

    def test_main_class_field_is_required(self):
        with self.assertRaises(IntegrityError):
            EASFactory(main_class=None)

    def test_name_field_is_required(self):
        with self.assertRaises(IntegrityError):
            EASFactory(name=None, main_class=self.enterprise)

    def test_short_name_field_is_required(self):
        with self.assertRaises(IntegrityError):
            EASFactory(short_name=None, main_class=self.enterprise)

    def test_successfully_created_with_minimal_requirements(self):
        subject = EASFactory(main_class=self.enterprise)
        self.assertIsNotNone(subject.pk)

    def test_main_class_relationship(self):
        subject = EASFactory(main_class=self.enterprise)
        self.assertIn(subject, self.enterprise.subjects_by_class.all())

    def test_main_subject_relationship(self):
        subject = EASFactory(main_class=self.enterprise)
        child = EASFactory(main_class=self.workshop, main_subject=subject)
        subject.refresh_from_db()
        self.assertIn(child, subject.children.all())

    def test_string_representation(self):
        subject = EASFactory(main_class=self.enterprise, name="test name")
        self.assertEqual(str(subject), "test name")

    def test_main_subject_deletion_causes_cascade_deletion_of_child_objects(self):
        EASFactory(main_class=self.enterprise)
        self.enterprise.delete()
        self.assertEqual(EconomicActivitySubject.objects.count(), 0)

    def test_main_class_deletion_causes_cascade_deletion_of_child_objects(self):
        subject = EASFactory(main_class=self.enterprise)
        EASFactory(main_class=self.workshop, main_subject=subject)
        subject.delete()
        self.assertEqual(EconomicActivitySubject.objects.count(), 0)


class GroupWorkingCenterTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.eas = EASFactory(main_class=cls.enterprise)
        cls.name = "СБОРОЧНЫЙ СТЕНД"
        cls.short_name = "B-4000 HV"
        cls.place = 5

    def test_name_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GWCFactory(name=None, main_class=self.means_of_labor, eas=self.eas, place=self.place)

    def test_short_name_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GWCFactory(short_name=None, main_class=self.means_of_labor, eas=self.eas, place=self.place)

    def test_main_class_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GWCFactory(main_class=None, eas=self.eas, place=self.place)

    def test_eas_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GWCFactory(eas=None, main_class=self.means_of_labor, place=self.place)

    def test_place_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GWCFactory(place=None, main_class=self.means_of_labor, eas=self.eas)

    def test_instance_was_successfully_created_with_minimal_requirements(self):
        center = GWCFactory(main_class=self.means_of_labor, eas=self.eas, place=self.place)
        self.assertIsNotNone(center.pk)

    def test_main_class_relationship(self):
        center = GWCFactory(main_class=self.means_of_labor, eas=self.eas, place=self.place)
        self.assertIn(center, self.means_of_labor.working_centers_by_class.all())

    def test_eas_relationship(self):
        center = GWCFactory(main_class=self.means_of_labor, eas=self.eas, place=self.place)
        self.assertIn(center, self.eas.working_centers_by_subject.all())

    def test_main_class_deletion_causes_cascade_deletion_of_child_objects(self):
        GWCFactory(main_class=self.means_of_labor, eas=self.eas, place=self.place)
        self.means_of_labor.delete()
        self.assertEqual(GroupWorkingCenter.objects.count(), 0)

    def test_eas_deletion_causes_cascade_deletion_of_child_objects(self):
        GWCFactory(main_class=self.means_of_labor, eas=self.eas, place=self.place)
        self.eas.delete()
        self.assertEqual(GroupWorkingCenter.objects.count(), 0)

    def test_string_representation(self):
        center = GWCFactory(name=self.name, main_class=self.means_of_labor, eas=self.eas, place=self.place)
        self.assertEqual(str(center), self.name)


class ProdOperationTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.eas = EASFactory(main_class=cls.enterprise)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStructFactory(main_class=cls.nuts_class)

        cls.product = ProdFactory(class_field=cls.nuts_subclass, image=None)

        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.operation = ClassStruct.objects.get(pk=OperationConsts.WELDING)

        cls.gwc = GWCFactory(main_class=cls.means_of_labor, eas=cls.eas, place=1)

        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)
        cls.num_of_workers = 1
        cls.t_pz = 1.0
        cls.t_sht = 1.0

    def _create_instance(self) -> ProdOperation:
        return ProdOperationFactory(
            prod=self.product,
            tech_oper=self.operation,
            profession=self.profession,
            center=self.gwc,
            qualification=self.qualification,
            num_of_workers=self.num_of_workers,
            t_pz=self.t_pz,
            t_sht=self.t_sht,
        )

    def test_prod_field_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationFactory(prod=None, tech_oper=self.operation, profession=self.profession,
                                 center=self.gwc, qualification=self.qualification)

    def test_tech_oper_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationFactory(prod=self.product, tech_oper=None, profession=self.profession,
                                 center=self.gwc, qualification=self.qualification)

    def test_profession_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationFactory(prod=self.product, tech_oper=self.operation, profession=None,
                                 center=self.gwc, qualification=self.qualification)

    def test_center_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationFactory(prod=self.product, tech_oper=self.operation, profession=self.profession,
                                 center=None, qualification=self.qualification)

    def test_qualification_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationFactory(prod=self.product, tech_oper=self.operation, profession=self.profession,
                                 center=self.gwc, qualification=None)

    def test_instance_was_successfully_created_with_minimal_requirements(self):
        prod_oper = self._create_instance()
        self.assertIsNotNone(prod_oper.pk)

    def test_t_pz_and_t_sht_default_values(self):
        prod_oper = ProdOperationFactory(
            prod=self.product, tech_oper=self.operation, profession=self.profession,
            center=self.gwc, qualification=self.qualification,
            t_pz = 1, t_sht = 1,
        )
        self.assertEqual(prod_oper.t_pz, ProdOperConsts.T_PZ_DEFAULT)
        self.assertEqual(prod_oper.t_sht, ProdOperConsts.T_SHT_DEFAULT)

    def test_prod_relationship(self):
        prod_oper = self._create_instance()
        self.assertIn(prod_oper, self.product.prod_operations.all())

    def test_tech_oper_relationship(self):
        prod_oper = self._create_instance()
        self.assertIn(prod_oper, self.operation.tech_operations.all())

    def test_profession_relationship(self):
        prod_oper = self._create_instance()
        self.assertIn(prod_oper, self.profession.profession_operations.all())

    def test_center_relationship(self):
        prod_oper = self._create_instance()
        self.assertIn(prod_oper, self.gwc.center_operations.all())

    def test_qualification_relationship(self):
        prod_oper = self._create_instance()
        self.assertIn(prod_oper, self.qualification.qualification_operations.all())

    def test_prod_deletion_causes_cascade_deletion_of_child_objects(self):
        self._create_instance()
        self.product.delete()
        self.assertEqual(ProdOperation.objects.count(), 0)

    def test_tech_oper_deletion_causes_cascade_deletion_of_child_objects(self):
        self._create_instance()
        self.operation.delete()
        self.assertEqual(ProdOperation.objects.count(), 0)

    def test_profession_deletion_causes_cascade_deletion_of_child_objects(self):
        self._create_instance()
        self.profession.delete()
        self.assertEqual(ProdOperation.objects.count(), 0)

    def test_center_deletion_causes_cascade_deletion_of_child_objects(self):
        self._create_instance()
        self.gwc.delete()
        self.assertEqual(ProdOperation.objects.count(), 0)

    def test_qualification_deletion_causes_cascade_deletion_of_child_objects(self):
        self._create_instance()
        self.qualification.delete()
        self.assertEqual(ProdOperation.objects.count(), 0)

    def test_string_representation(self):
        prod_oper = self._create_instance()
        expected = f"{self.product.name} - {self.operation.name}"
        self.assertEqual(str(prod_oper), expected)


class ProdOperationPosTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.eas = EASFactory(main_class=cls.enterprise)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStructFactory(main_class=cls.nuts_class)

        cls.product1 = ProdFactory(class_field=cls.nuts_subclass, image=None)
        cls.product2 = ProdFactory(class_field=cls.nuts_subclass, image=None)

        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.operation = ClassStruct.objects.get(pk=OperationConsts.WELDING)

        cls.gwc = GWCFactory(main_class=cls.means_of_labor, eas=cls.eas, place=1)

        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)
        cls.num_of_workers = 1
        cls.t_pz = 1.0
        cls.t_sht = 1.0

        cls.prod_oper1 = ProdOperationFactory(
            prod=cls.product1, tech_oper=cls.operation, profession=cls.profession,
            center=cls.gwc, qualification=cls.qualification,
            num_of_workers=cls.num_of_workers, t_pz=cls.t_pz, t_sht=cls.t_sht,
        )
        cls.prod_oper2 = ProdOperationFactory(
            prod=cls.product2, tech_oper=cls.operation, profession=cls.profession,
            center=cls.gwc, qualification=cls.qualification,
            num_of_workers=cls.num_of_workers, t_pz=cls.t_pz, t_sht=cls.t_sht,
        )

        cls.input_quantity = ProdOperationPosConsts.MIN_VALUE + 1
        cls.output_quantity = cls.input_quantity + 1
        cls.n_input_quantity = ProdOperationPosConsts.MIN_VALUE - 2
        cls.n_output_quantity = cls.n_input_quantity + 1

    def _create_instance(self):
        return ProdOperationPosFactory(
            input_prod_oper=self.prod_oper1,
            output_prod_oper=self.prod_oper2,
            input_quantity=self.input_quantity,
            output_quantity=self.output_quantity,
        )

    def test_input_prod_oper_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationPosFactory(input_prod_oper=None, output_prod_oper=self.prod_oper2)

    def test_output_prod_oper_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationPosFactory(input_prod_oper=self.prod_oper1, output_prod_oper=None)

    def test_input_quantity_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationPosFactory(input_prod_oper=self.prod_oper1, output_prod_oper=self.prod_oper2, input_quantity=None)

    def test_output_quantity_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperationPosFactory(input_prod_oper=self.prod_oper1, output_prod_oper=self.prod_oper2, output_quantity=None)

    def test_input_quantity_should_be_positive(self):
        pos = ProdOperationPosFactory.build(
            input_prod_oper=self.prod_oper1, output_prod_oper=self.prod_oper2,
            input_quantity=self.n_input_quantity, output_quantity=self.output_quantity,
        )
        with self.assertRaises(ValidationError):
            pos.full_clean()

    def test_output_quantity_should_be_positive(self):
        pos = ProdOperationPosFactory.build(
            input_prod_oper=self.prod_oper1, output_prod_oper=self.prod_oper2,
            input_quantity=self.input_quantity, output_quantity=self.n_output_quantity,
        )
        with self.assertRaises(ValidationError):
            pos.full_clean()

    def test_input_prod_oper_deletion_causes_cascade_deletion_of_child_objects(self):
        self._create_instance()
        self.prod_oper1.delete()
        self.assertEqual(ProdOperationPos.objects.count(), 0)

    def test_output_prod_oper_deletion_causes_cascade_deletion_of_child_objects(self):
        self._create_instance()
        self.prod_oper2.delete()
        self.assertEqual(ProdOperationPos.objects.count(), 0)

    def test_string_representation(self):
        prod_oper = self._create_instance()
        expected = (
            f"<{self.product1.name} - {self.operation.name}> - "
            f"<{self.product2.name} - {self.operation.name}> "
            f"({self.input_quantity} -> {self.output_quantity})"
        )
        self.assertEqual(str(prod_oper), expected)
