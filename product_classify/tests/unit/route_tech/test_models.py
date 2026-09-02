from django.db import IntegrityError

from classes.models import ClassStruct
from classes.constants import MetaConsts

from route_tech.models import (
    EconomicActivitySubject,
    GroupWorkingCenter,
)

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
