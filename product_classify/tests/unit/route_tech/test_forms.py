from django.db.models import QuerySet
from faker import Faker

from classes.models import ClassStruct
from classes.constants import MetaConsts

from route_tech.constants import EASConsts
from route_tech.errors import EASErrors
from route_tech.models import EconomicActivitySubject
from route_tech.forms import EconomicActivitySubjectForm

from tests.unit.base import BaseUnitTestCase


class EconomicActivitySubjectFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.name = cls.faker.name()[:EASConsts.NAME_MAX_LENGTH]
        cls.short_name = cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH]
        cls.new_name = cls.faker.name()[:EASConsts.NAME_MAX_LENGTH]
        cls.new_short_name = cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH]
        cls.main_subject = EconomicActivitySubject.objects.create(
            name=cls.name,
            short_name=cls.short_name,
            main_class=cls.enterprise,
            main_subject=None
        )
        cls.valid_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": None
        }
        cls.update_data = {
            "name": cls.new_name,
            "short_name": cls.new_short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": cls.main_subject.pk
        }
        cls.empty_name_data = {
            "name": None,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": None
        }
        cls.empty_short_name_data = {
            "name": cls.name,
            "short_name": None,
            "main_class": cls.enterprise.pk,
            "main_subject": None
        }
        cls.empty_main_class_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": None,
            "main_subject": None            
        }
        cls.empty_main_subject_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": None            
        }
        cls.valid_data_with_main_subject = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "main_subject": cls.main_subject.pk
        }

    def test_main_class_queryset(self):
        form = EconomicActivitySubjectForm()
        queryset = form.fields["main_class"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(len(queryset), 3)

    def test_main_subject_queryset(self):
        form = EconomicActivitySubjectForm()
        queryset = form.fields["main_subject"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(len(queryset), 1)

    def test_name_field_is_required(self):
        form = EconomicActivitySubjectForm(self.empty_name_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["name"][0],
            EASErrors.EMPTY_NAME,
        )

    def test_short_name_field_is_required(self):
        form = EconomicActivitySubjectForm(self.empty_short_name_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["short_name"][0],
            EASErrors.EMPTY_SHORT_NAME
        )

    def test_main_class_field_is_required(self):
        form = EconomicActivitySubjectForm(self.empty_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["main_class"][0],
            EASErrors.EMPTY_MAIN_CLASS
        )

    def test_main_subject_field_is_optional(self):
        form = EconomicActivitySubjectForm(self.empty_main_subject_data)
        self.assertTrue(form.is_valid())

    def test_valid_form_data(self):
        form = EconomicActivitySubjectForm(self.valid_data)
        self.assertTrue(form.is_valid())

    def test_economic_activity_subject_is_saved_successfully(self):
        form = EconomicActivitySubjectForm(self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertIsNotNone(instance.pk)
        self.assertEqual(instance.name, self.valid_data["name"])
        self.assertEqual(instance.short_name, self.valid_data["short_name"])
        self.assertEqual(instance.main_class.pk, self.valid_data["main_class"])

    def test_economic_activity_subject_is_updated_successfully(self):
        form = EconomicActivitySubjectForm(self.valid_data)
        self.assertTrue(form.is_valid())

        instance = form.save()

        form = EconomicActivitySubjectForm(self.update_data, instance=instance)
        self.assertTrue(form.is_valid())

        updated_instance = form.save()
        self.assertEqual(instance.pk, updated_instance.pk)
        self.assertEqual(updated_instance.name, self.update_data["name"])
        self.assertEqual(updated_instance.short_name, self.update_data["short_name"])
        self.assertEqual(updated_instance.main_class.pk, self.update_data["main_class"])
        self.assertEqual(updated_instance.main_subject.pk, self.update_data["main_subject"])
