from django.db.models import QuerySet
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker
from PIL import Image
from io import BytesIO
from decimal import Decimal

from classes.models import ClassStruct
from classes.constants import MetaConsts, ProfessionConsts, QualificationConsts, OperationConsts
from classes.constants import ProductsConsts

from products.models import Prod

from route_tech.constants import EASConsts, GWCConsts, ProdOperationPosConsts
from route_tech.errors import EASErrors, GWCErrors, ProdOperErrors, ProdOperationPosErrors
from route_tech.models import EconomicActivitySubject, GroupWorkingCenter, ProdOperation
from route_tech.forms import EconomicActivitySubjectForm, GroupWorkingCenterForm, ProdOperationForm, ProdOperationPosForm

from tests.unit.base import BaseUnitTestCase


def create_image(extension: str = "jpg"):
    image = Image.new("RGB", (100, 100), "red")
    file = BytesIO()
    format = "JPEG" if extension == "jpg" else "PNG"
    image.save(file, format)
    file.seek(0)
    return SimpleUploadedFile(
        f"test.{extension}",
        file.read(),
        content_type=f"image/{extension if extension != 'jpg' else 'jpeg'}",
    )


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


class GroupWorkingCenterFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.enterprise = ClassStruct.objects.create(
            name="Means of labor 1",
            short_name="MeansL1",
            main_class=cls.means_of_labor
        )
        cls.department = ClassStruct.objects.create(
            name="Department 1",
            short_name="Dept1",
            main_class=cls.means_of_labor,
        )
        cls.another_department = ClassStruct.objects.create(
            name="Department 2",
            short_name="Dept2",
            main_class=cls.means_of_labor,
        )

        cls.eas1 = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None,
        )
        cls.eas2 = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=cls.eas1,
        )

        cls.name = cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH]
        cls.short_name = cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH]
        cls.new_name = cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH]
        cls.new_short_name = cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH]
        cls.place = cls.faker.random_int(min=1, max=100)

        cls.valid_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "eas": cls.eas1.pk,
            "place": cls.place,
        }

        cls.update_data = {
            "name": cls.new_name,
            "short_name": cls.new_short_name,
            "main_class": cls.department.pk,
            "eas": cls.eas2.pk,
            "place": cls.place + 10,
        }

        cls.empty_name_data = {
            "name": "",
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "eas": cls.eas1.pk,
            "place": cls.place,
        }

        cls.empty_short_name_data = {
            "name": cls.name,
            "short_name": "",
            "main_class": cls.enterprise.pk,
            "eas": cls.eas1.pk,
            "place": cls.place,
        }

        cls.empty_main_class_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": None,
            "eas": cls.eas1.pk,
            "place": cls.place,
        }

        cls.empty_eas_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "eas": None,
            "place": cls.place,
        }

        cls.empty_place_data = {
            "name": cls.name,
            "short_name": cls.short_name,
            "main_class": cls.enterprise.pk,
            "eas": cls.eas1.pk,
            "place": None,
        }

    def test_main_class_queryset(self):
        form = GroupWorkingCenterForm()
        queryset = form.fields["main_class"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(queryset.count(), 3)

    def test_eas_queryset(self):
        form = GroupWorkingCenterForm()
        queryset = form.fields["eas"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(queryset.count(), 2)

    def test_name_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_name_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["name"][0],
            GWCErrors.EMPTY_NAME,
        )

    def test_short_name_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_short_name_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["short_name"][0],
            GWCErrors.EMPTY_SHORT_NAME,
        )

    def test_main_class_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["main_class"][0],
            GWCErrors.EMPTY_MAIN_CLASS,
        )

    def test_eas_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_eas_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["eas"][0],
            GWCErrors.EMPTY_EAS,
        )

    def test_place_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_place_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["place"][0],
            GWCErrors.EMPTY_PLACE,
        )

    def test_valid_form_data(self):
        form = GroupWorkingCenterForm(self.valid_data)
        self.assertTrue(form.is_valid())

    def test_group_working_center_is_saved_successfully(self):
        form = GroupWorkingCenterForm(self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertIsNotNone(instance.pk)
        self.assertEqual(instance.name, self.valid_data["name"])
        self.assertEqual(instance.short_name, self.valid_data["short_name"])
        self.assertEqual(instance.main_class.pk, self.valid_data["main_class"])
        self.assertEqual(instance.eas.pk, self.valid_data["eas"])
        self.assertEqual(instance.place, self.valid_data["place"])

    def test_group_working_center_is_updated_successfully(self):
        form = GroupWorkingCenterForm(self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save()

        form = GroupWorkingCenterForm(self.update_data, instance=instance)
        self.assertTrue(form.is_valid())
        updated_instance = form.save()

        self.assertEqual(instance.pk, updated_instance.pk)
        self.assertEqual(updated_instance.name, self.update_data["name"])
        self.assertEqual(updated_instance.short_name, self.update_data["short_name"])
        self.assertEqual(updated_instance.main_class.pk, self.update_data["main_class"])
        self.assertEqual(updated_instance.eas.pk, self.update_data["eas"])
        self.assertEqual(updated_instance.place, self.update_data["place"])


class ProdOperationFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name="Nuts subclass",
            short_name="nuts subcls",
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.stand = ClassStruct.objects.create(
            name="Assembly stand",
            short_name="stand",
            main_class=cls.means_of_labor,
            base_ei=None,
        )
        
        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)
        
        # Создаем субъект экономической деятельности (для GroupWorkingCenter)
        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None,
        )
        
        # Создаем GroupWorkingCenter
        cls.center = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=20),
        )
        
        # Создаем изделие (Prod)
        cls.prod = Prod.objects.create(
            name=cls.faker.name()[:100],
            short_name=cls.faker.name()[:50],
            class_field=cls.nuts_subclass,
            image=create_image(),
        )
        
        # Генерируем данные для формы
        cls.num_of_workers = cls.faker.random_int(min=1, max=5)
        cls.t_pz = round(cls.faker.random_number(digits=2, fix_len=False) + 0.1, 2)
        cls.t_sht = round(cls.faker.random_number(digits=2, fix_len=False) + 0.1, 2)
        
        cls.valid_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.num_of_workers,
            "t_pz": cls.t_pz,
            "t_sht": cls.t_sht,
        }
        
        cls.update_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.num_of_workers + 1,
            "t_pz": cls.t_pz + 0.5,
            "t_sht": cls.t_sht + 0.5,
        }
        
        # Данные с пустыми значениями для проверки required
        cls.empty_prod_data = {
            "prod": None,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.num_of_workers,
            "t_pz": cls.t_pz,
            "t_sht": cls.t_sht,
        }
        
        cls.empty_tech_oper_data = {
            "prod": cls.prod.pk,
            "tech_oper": None,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.num_of_workers,
            "t_pz": cls.t_pz,
            "t_sht": cls.t_sht,
        }
        
        cls.empty_profession_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": None,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.num_of_workers,
            "t_pz": cls.t_pz,
            "t_sht": cls.t_sht,
        }
        
        cls.empty_center_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": None,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.num_of_workers,
            "t_pz": cls.t_pz,
            "t_sht": cls.t_sht,
        }
        
        cls.empty_qualification_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": None,
            "num_of_workers": cls.num_of_workers,
            "t_pz": cls.t_pz,
            "t_sht": cls.t_sht,
        }
        
        cls.empty_num_of_workers_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": None,
            "t_pz": cls.t_pz,
            "t_sht": cls.t_sht,
        }
        
        cls.empty_t_pz_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.num_of_workers,
            "t_pz": None,
            "t_sht": cls.t_sht,
        }
        
        cls.empty_t_sht_data = {
            "prod": cls.prod.pk,
            "tech_oper": cls.tech_oper.pk,
            "profession": cls.profession.pk,
            "center": cls.center.pk,
            "qualification": cls.qualification.pk,
            "num_of_workers": cls.num_of_workers,
            "t_pz": cls.t_pz,
            "t_sht": None,
        }

    def test_prod_queryset(self):
        form = ProdOperationForm()
        queryset = form.fields["prod"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(queryset.count(), 1) 

    def test_tech_oper_queryset(self):
        form = ProdOperationForm()
        queryset = form.fields["tech_oper"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertIn(self.tech_oper, queryset)

    def test_profession_queryset(self):
        form = ProdOperationForm()
        queryset = form.fields["profession"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertIn(self.profession, queryset)

    def test_center_queryset(self):
        form = ProdOperationForm()
        queryset = form.fields["center"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertIn(self.center, queryset)

    def test_qualification_queryset(self):
        form = ProdOperationForm()
        queryset = form.fields["qualification"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertIn(self.qualification, queryset)

    def test_prod_field_is_required(self):
        form = ProdOperationForm(self.empty_prod_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["prod"][0],
            ProdOperErrors.EMPTY_PROD,
        )

    def test_tech_oper_field_is_required(self):
        form = ProdOperationForm(self.empty_tech_oper_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["tech_oper"][0],
            ProdOperErrors.EMPTY_TECH_OPER,
        )

    def test_profession_field_is_required(self):
        form = ProdOperationForm(self.empty_profession_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["profession"][0],
            ProdOperErrors.EMPTY_PROFESSION,
        )

    def test_center_field_is_required(self):
        form = ProdOperationForm(self.empty_center_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["center"][0],
            ProdOperErrors.EMPTY_CENTER,
        )

    def test_qualification_field_is_required(self):
        form = ProdOperationForm(self.empty_qualification_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["qualification"][0],
            ProdOperErrors.EMPTY_QUALIFICATION,
        )

    def test_num_of_workers_field_is_required(self):
        form = ProdOperationForm(self.empty_num_of_workers_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["num_of_workers"][0],
            ProdOperErrors.EMPTY_NUM_WORKERS,
        )

    def test_t_pz_field_is_required(self):
        form = ProdOperationForm(self.empty_t_pz_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["t_pz"][0],
            "Обязательное поле.",
        )

    def test_t_sht_field_is_required(self):
        form = ProdOperationForm(self.empty_t_sht_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["t_sht"][0],
            "Обязательное поле.",
        )

    def test_valid_form_data(self):
        form = ProdOperationForm(self.valid_data)
        self.assertTrue(form.is_valid())

    def test_prod_operation_is_saved_successfully(self):
        form = ProdOperationForm(self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertIsNotNone(instance.pk)
        self.assertEqual(instance.prod.pk, self.valid_data["prod"])
        self.assertEqual(instance.tech_oper.pk, self.valid_data["tech_oper"])
        self.assertEqual(instance.profession.pk, self.valid_data["profession"])
        self.assertEqual(instance.center.pk, self.valid_data["center"])
        self.assertEqual(instance.qualification.pk, self.valid_data["qualification"])
        self.assertEqual(instance.num_of_workers, self.valid_data["num_of_workers"])
        self.assertEqual(instance.t_pz, self.valid_data["t_pz"])
        self.assertEqual(instance.t_sht, self.valid_data["t_sht"])

    def test_prod_operation_is_updated_successfully(self):
        form = ProdOperationForm(self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save()

        form = ProdOperationForm(self.update_data, instance=instance)
        self.assertTrue(form.is_valid())
        updated_instance = form.save()

        self.assertEqual(instance.pk, updated_instance.pk)
        self.assertEqual(updated_instance.prod.pk, self.update_data["prod"])
        self.assertEqual(updated_instance.tech_oper.pk, self.update_data["tech_oper"])
        self.assertEqual(updated_instance.profession.pk, self.update_data["profession"])
        self.assertEqual(updated_instance.center.pk, self.update_data["center"])
        self.assertEqual(updated_instance.qualification.pk, self.update_data["qualification"])
        self.assertEqual(updated_instance.num_of_workers, self.update_data["num_of_workers"])
        self.assertEqual(updated_instance.t_pz, self.update_data["t_pz"])
        self.assertEqual(updated_instance.t_sht, self.update_data["t_sht"])


class ProdOperationPosFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.nuts_subclass = ClassStruct.objects.create(
            name="Nuts subclass",
            short_name="nuts subcls",
            base_ei=None,
            main_class=cls.nuts_class,
        )
        cls.stand = ClassStruct.objects.create(
            name="Assembly stand",
            short_name="stand",
            main_class=cls.means_of_labor,
            base_ei=None,
        )

        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.eas = EconomicActivitySubject.objects.create(
            name=cls.faker.name()[:EASConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:EASConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.enterprise,
            main_subject=None,
        )

        cls.center = GroupWorkingCenter.objects.create(
            name=cls.faker.name()[:GWCConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:GWCConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.stand,
            eas=cls.eas,
            place=cls.faker.random_int(min=1, max=20),
        )

        cls.prod_input = Prod.objects.create(
            name=cls.faker.name()[:100],
            short_name=cls.faker.name()[:50],
            class_field=cls.nuts_subclass,
            image=create_image(),
        )
        cls.prod_output = Prod.objects.create(
            name=cls.faker.name()[:100],
            short_name=cls.faker.name()[:50],
            class_field=cls.nuts_subclass,
            image=create_image(),
        )

        cls.input_prod_oper = ProdOperation.objects.create(
            prod=cls.prod_input,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=cls.faker.random_int(min=1, max=5),
            t_pz=round(cls.faker.random_number(digits=2, fix_len=False) + 0.1, 2),
            t_sht=round(cls.faker.random_number(digits=2, fix_len=False) + 0.1, 2),
        )
        cls.output_prod_oper = ProdOperation.objects.create(
            prod=cls.prod_output,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=cls.faker.random_int(min=1, max=5),
            t_pz=round(cls.faker.random_number(digits=2, fix_len=False) + 0.1, 2),
            t_sht=round(cls.faker.random_number(digits=2, fix_len=False) + 0.1, 2),
        )

        cls.input_quantity = Decimal(
            cls.faker.random_number(digits=2, fix_len=False) + 0.1
        ).quantize(Decimal('0.01'))
        cls.output_quantity = Decimal(
            cls.faker.random_number(digits=2, fix_len=False) + 0.1
        ).quantize(Decimal('0.01'))

        min_val = ProdOperationPosConsts.MIN_VALUE
        if cls.input_quantity < min_val:
            cls.input_quantity += min_val
        if cls.output_quantity < min_val:
            cls.output_quantity += min_val

        cls.valid_data = {
            "input_prod_oper": cls.input_prod_oper.pk,
            "output_prod_oper": cls.output_prod_oper.pk,
            "input_quantity": cls.input_quantity,
            "output_quantity": cls.output_quantity,
        }

        cls.update_data = {
            "input_prod_oper": cls.input_prod_oper.pk,
            "output_prod_oper": cls.output_prod_oper.pk,
            "input_quantity": cls.input_quantity + Decimal('0.5'),
            "output_quantity": cls.output_quantity + Decimal('0.5'),
        }

        cls.empty_input_prod_oper_data = {
            "input_prod_oper": None,
            "output_prod_oper": cls.output_prod_oper.pk,
            "input_quantity": cls.input_quantity,
            "output_quantity": cls.output_quantity,
        }
        cls.empty_output_prod_oper_data = {
            "input_prod_oper": cls.input_prod_oper.pk,
            "output_prod_oper": None,
            "input_quantity": cls.input_quantity,
            "output_quantity": cls.output_quantity,
        }
        cls.empty_input_quantity_data = {
            "input_prod_oper": cls.input_prod_oper.pk,
            "output_prod_oper": cls.output_prod_oper.pk,
            "input_quantity": None,
            "output_quantity": cls.output_quantity,
        }
        cls.empty_output_quantity_data = {
            "input_prod_oper": cls.input_prod_oper.pk,
            "output_prod_oper": cls.output_prod_oper.pk,
            "input_quantity": cls.input_quantity,
            "output_quantity": None,
        }

        cls.invalid_input_quantity_data = {
            "input_prod_oper": cls.input_prod_oper.pk,
            "output_prod_oper": cls.output_prod_oper.pk,
            "input_quantity": Decimal('-0.1'),
            "output_quantity": cls.output_quantity,
        }
        cls.invalid_output_quantity_data = {
            "input_prod_oper": cls.input_prod_oper.pk,
            "output_prod_oper": cls.output_prod_oper.pk,
            "input_quantity": cls.input_quantity,
            "output_quantity": Decimal('-0.1'),
        }

    def test_input_prod_oper_queryset(self):
        form = ProdOperationPosForm()
        queryset = form.fields["input_prod_oper"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertIn(self.input_prod_oper, queryset)

    def test_output_prod_oper_queryset(self):
        form = ProdOperationPosForm()
        queryset = form.fields["output_prod_oper"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertIn(self.output_prod_oper, queryset)

    def test_input_prod_oper_field_is_required(self):
        form = ProdOperationPosForm(self.empty_input_prod_oper_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["input_prod_oper"][0],
            ProdOperationPosErrors.EMPTY_INPUT_PROD_OPER,
        )

    def test_output_prod_oper_field_is_required(self):
        form = ProdOperationPosForm(self.empty_output_prod_oper_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["output_prod_oper"][0],
            ProdOperationPosErrors.EMPTY_OUTPUT_PROD_OPER,
        )

    def test_input_quantity_field_is_required(self):
        form = ProdOperationPosForm(self.empty_input_quantity_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["input_quantity"][0],
            ProdOperationPosErrors.EMPTY_INPUT_QUANTITY,
        )

    def test_output_quantity_field_is_required(self):
        form = ProdOperationPosForm(self.empty_output_quantity_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["output_quantity"][0],
            ProdOperationPosErrors.EMPTY_OUTPUT_QUANTITY,
        )

    def test_input_quantity_min_value_validation(self):
        form = ProdOperationPosForm(self.invalid_input_quantity_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Значение не может быть меньше",
            form.errors["input_quantity"][0]
        )

    def test_output_quantity_min_value_validation(self):
        form = ProdOperationPosForm(self.invalid_output_quantity_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Значение не может быть меньше",
            form.errors["output_quantity"][0]
        )

    def test_valid_form_data(self):
        form = ProdOperationPosForm(self.valid_data)
        self.assertTrue(form.is_valid())

    def test_prod_operation_pos_is_saved_successfully(self):
        form = ProdOperationPosForm(self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertIsNotNone(instance.pk)
        self.assertEqual(instance.input_prod_oper.pk, self.valid_data["input_prod_oper"])
        self.assertEqual(instance.output_prod_oper.pk, self.valid_data["output_prod_oper"])
        self.assertEqual(instance.input_quantity, self.valid_data["input_quantity"])
        self.assertEqual(instance.output_quantity, self.valid_data["output_quantity"])

    def test_prod_operation_pos_is_updated_successfully(self):
        form = ProdOperationPosForm(self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save()

        form = ProdOperationPosForm(self.update_data, instance=instance)
        self.assertTrue(form.is_valid())
        updated_instance = form.save()

        self.assertEqual(instance.pk, updated_instance.pk)
        self.assertEqual(updated_instance.input_prod_oper.pk, self.update_data["input_prod_oper"])
        self.assertEqual(updated_instance.output_prod_oper.pk, self.update_data["output_prod_oper"])
        self.assertEqual(updated_instance.input_quantity, self.update_data["input_quantity"])
        self.assertEqual(updated_instance.output_quantity, self.update_data["output_quantity"])
