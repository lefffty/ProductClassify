from django.db import IntegrityError
from faker import Faker

from classes.models import ClassStruct
from classes.constants import (
    MetaConsts,
    OperationConsts,
    ProductsConsts,
    ProfessionConsts,
    QualificationConsts,
)
from products.models import Prod

from route_tech.models import (
    EconomicActivitySubject,
    GroupWorkingCenter,
    ProdOperation,
)
from route_tech.constants import ProdOperConsts

from tests.unit.base import BaseUnitTestCase


class EconomicActivityEntityTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.workshop = ClassStruct.objects.get(pk=MetaConsts.WORKSHOP)

    def test_main_class_field_is_required(self):
        with self.assertRaises(IntegrityError):
            EconomicActivitySubject.objects.create(
                name="test name",
                short_name="test short",
                main_class=None,
                main_subject=None
            )

    def test_name_field_is_required(self):
        with self.assertRaises(IntegrityError):
            EconomicActivitySubject.objects.create(
                name=None,
                short_name="test short",
                main_class=self.enterprise,
                main_subject=None
            )

    def test_short_name_field_is_required(self):
        with self.assertRaises(IntegrityError):
            EconomicActivitySubject.objects.create(
                name="test name",
                short_name=None,
                main_class=self.enterprise,
                main_subject=None
            )

    def test_successfully_created_with_minimal_requirements(self):
        subject = EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.enterprise,
            main_subject=None
        )
        self.assertGreater(EconomicActivitySubject.objects.count(), 0)
        self.assertIsNotNone(subject.pk)

    def test_main_class_relationship(self):
        subject = EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.enterprise,
            main_subject=None
        )
        self.assertIn(subject, self.enterprise.subjects_by_class.all())

    def test_main_subject_relationship(self):
        subject = EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.enterprise,
            main_subject=None
        )

        child = EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.workshop,
            main_subject=subject
        )
        subject.refresh_from_db()

        self.assertIn(child, subject.children.all())

    def test_string_representation(self):
        subject = EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.enterprise,
            main_subject=None
        )
        self.assertEqual(str(subject), "test name")

    def test_main_subject_deletion_causes_cascade_deletion_of_child_objects(self):
        EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.enterprise,
            main_subject=None
        )

        self.enterprise.delete()

        self.assertEqual(EconomicActivitySubject.objects.count(), 0)

    def test_main_class_deletion_causes_cascade_deletion_of_child_objects(self):
        subject = EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.enterprise,
            main_subject=None
        )

        EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.workshop,
            main_subject=subject
        )

        subject.delete()

        self.assertEqual(EconomicActivitySubject.objects.count(), 0)


class GroupWorkingCenterTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.eas = EconomicActivitySubject.objects.create(
            name="Цех 01",
            short_name="01",
            main_class=cls.enterprise,
            main_subject=None,
        )
        cls.name = "СБОРОЧНЫЙ СТЕНД"
        cls.short_name = "B-4000 HV"
        cls.place = 5

    def test_name_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GroupWorkingCenter.objects.create(
                name=None,
                short_name=self.short_name,
                main_class=self.means_of_labor,
                eas=self.eas,
                place=self.place,
            )

    def test_short_name_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GroupWorkingCenter.objects.create(
                name=self.name,
                short_name=None,
                main_class=self.means_of_labor,
                eas=self.eas,
                place=self.place,
            )

    def test_main_class_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GroupWorkingCenter.objects.create(
                name=self.name,
                short_name=self.short_name,
                main_class=None,
                eas=self.eas,
                place=self.place,
            )

    def test_eas_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GroupWorkingCenter.objects.create(
                name=self.name,
                short_name=self.short_name,
                main_class=self.means_of_labor,
                eas=None,
                place=self.place,
            )

    def test_place_field_is_required(self):
        with self.assertRaises(IntegrityError):
            GroupWorkingCenter.objects.create(
                name=self.name,
                short_name=self.short_name,
                main_class=self.means_of_labor,
                eas=self.eas,
                place=None,
            )

    def test_instance_was_successfully_created_with_minimal_requirements(self):
        center = GroupWorkingCenter.objects.create(
            name=self.name,
            short_name=self.short_name,
            main_class=self.means_of_labor,
            eas=self.eas,
            place=self.place,
        )

        self.assertIsNotNone(center.pk)

    def test_main_class_relationship(self):
        center = GroupWorkingCenter.objects.create(
            name=self.name,
            short_name=self.short_name,
            main_class=self.means_of_labor,
            eas=self.eas,
            place=self.place,
        )

        self.assertIn(center, self.means_of_labor.working_centers_by_class.all())

    def test_eas_relationship(self):
        center = GroupWorkingCenter.objects.create(
            name=self.name,
            short_name=self.short_name,
            main_class=self.means_of_labor,
            eas=self.eas,
            place=self.place,
        )

        self.assertIn(center, self.eas.working_centers_by_subject.all())

    def test_main_class_deletion_causes_cascade_deletion_of_child_objects(self):
        GroupWorkingCenter.objects.create(
            name=self.name,
            short_name=self.short_name,
            main_class=self.means_of_labor,
            eas=self.eas,
            place=self.place,
        )

        self.means_of_labor.delete()
        self.assertEqual(GroupWorkingCenter.objects.count(), 0)

    def test_eas_deletion_causes_cascade_deletion_of_child_objects(self):
        GroupWorkingCenter.objects.create(
            name=self.name,
            short_name=self.short_name,
            main_class=self.means_of_labor,
            eas=self.eas,
            place=self.place,
        )

        self.eas.delete()
        self.assertEqual(GroupWorkingCenter.objects.count(), 0)

    def test_string_representation(self):
        center = GroupWorkingCenter.objects.create(
            name=self.name,
            short_name=self.short_name,
            main_class=self.means_of_labor,
            eas=self.eas,
            place=self.place,
        )

        self.assertEqual(str(center), self.name)


class ProdOperationTest(BaseUnitTestCase):
    fixtures = [
        "ei.json",
        "classes.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.eas = EconomicActivitySubject.objects.create(
            name="Цех 01",
            short_name="01",
            main_class=cls.enterprise,
            main_subject=None,
        )
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.faker.name(),
            short_name=cls.faker.name(),
            base_ei=None,
            main_class=cls.nuts_class
        )
        # product
        prod_name = cls.faker.name()
        cls.product = Prod.objects.create(
            name=prod_name,
            short_name=cls.faker.name(),
            class_field=cls.nuts_subclass,
            image=None,
            cost=None,
            modification=None,
            ei=None,
        )
        # profession
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        # operation
        cls.operation = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        # group working center
        cls.gwc = GroupWorkingCenter.objects.create(
            name="СБОРОЧНЫЙ СТЕНД",
            short_name="B-4000 HV",
            main_class=cls.means_of_labor,
            eas=cls.eas,
            place=1,
        )
        # qualification
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)
        cls.num_of_workers = 1
        cls.t_pz = 1.0
        cls.t_sht = 1.0

    def _create_instance(self) -> ProdOperation:
        prod_oper = ProdOperation.objects.create(
            prod=self.product,
            tech_oper=self.operation,
            profession=self.profession,
            center=self.gwc,
            qualification=self.qualification,
            num_of_workers=self.num_of_workers,
            t_pz=self.t_pz,
            t_sht=self.t_sht,
        )
        return prod_oper

    def test_prod_field_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperation.objects.create(
                prod=None,
                tech_oper=self.operation,
                profession=self.profession,
                center=self.gwc,
                qualification=self.qualification,
                num_of_workers=self.num_of_workers,
                t_pz=self.t_pz,
                t_sht=self.t_sht,
            )

    def test_tech_oper_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperation.objects.create(
                prod=self.product,
                tech_oper=None,
                profession=self.profession,
                center=self.gwc,
                qualification=self.qualification,
                num_of_workers=self.num_of_workers,
                t_pz=self.t_pz,
                t_sht=self.t_sht,
            )

    def test_profession_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperation.objects.create(
                prod=self.product,
                tech_oper=self.operation,
                profession=None,
                center=self.gwc,
                qualification=self.qualification,
                num_of_workers=self.num_of_workers,
                t_pz=self.t_pz,
                t_sht=self.t_sht,
            )

    def test_center_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperation.objects.create(
                prod=self.product,
                tech_oper=self.operation,
                profession=self.profession,
                center=None,
                qualification=self.qualification,
                num_of_workers=self.num_of_workers,
                t_pz=self.t_pz,
                t_sht=self.t_sht,
            )

    def test_qualification_is_required(self):
        with self.assertRaises(IntegrityError):
            ProdOperation.objects.create(
                prod=self.product,
                tech_oper=self.operation,
                profession=self.profession,
                center=self.gwc,
                qualification=None,
                num_of_workers=self.num_of_workers,
                t_pz=self.t_pz,
                t_sht=self.t_sht,
            )

    def test_instance_was_successfully_created_with_minimal_requirements(self):
        prod_oper = self._create_instance()

        self.assertIsNotNone(prod_oper.pk)

    def test_t_pz_and_t_sht_default_values(self):
        prod_oper = self._create_instance()

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

    def test_qualifiaction_relationship(self):
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
