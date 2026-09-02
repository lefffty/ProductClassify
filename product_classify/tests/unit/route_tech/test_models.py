from django.db import IntegrityError

from classes.models import ClassStruct
from classes.constants import MetaConsts

from route_tech.models import EconomicActivitySubject

from tests.unit.base import BaseUnitTestCase


class EconomicActivityEntityTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.class_po = ClassStruct.objects.get(pk=MetaConsts.SUBJECT_AREA_CLASS)
        cls.economic_activity_subject = ClassStruct.objects.create(
            name="Субъект хозяйственной деятельности",
            short_name="СХД",
            main_class=cls.class_po,
            base_ei=None,
        )
        cls.enterprise = ClassStruct.objects.create(
            name="ПРОИЗВОДСТВЕННОЕ ПРЕДПРИЯТИЕ",
            short_name="ПР. ПРЕД.",
            main_class=cls.economic_activity_subject,
            base_ei=None,
        )
        cls.workshop = ClassStruct.objects.create(
            name="ЦЕХ",
            short_name="ЦЕХ",
            main_class=cls.economic_activity_subject,
            base_ei=None
        )

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

    def test_main_subject_deletion_causes_cascade_deletion_of_child_elements(self):
        EconomicActivitySubject.objects.create(
            name="test name",
            short_name="test short",
            main_class=self.enterprise,
            main_subject=None
        )

        self.enterprise.delete()

        self.assertEqual(EconomicActivitySubject.objects.count(), 0)

    def test_main_class_deletion_causes_cascade_deletion_of_child_elements(self):
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
