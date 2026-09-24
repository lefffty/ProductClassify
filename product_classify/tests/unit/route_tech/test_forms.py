from django.db.models import QuerySet
from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image
from io import BytesIO
from decimal import Decimal

from classes.models import ClassStruct
from classes.constants import MetaConsts, ProfessionConsts, QualificationConsts, OperationConsts
from classes.constants import ProductsConsts

from tests.unit.classes.factories.class_struct import ClassStructFactory
from tests.unit.products.factories.product import ProdFactory
from tests.unit.route_tech.factories.eas import EASFactory, EASFormData
from tests.unit.route_tech.factories.gwc import GWCFactory, GWCFormData
from tests.unit.route_tech.factories.prod_oper import ProdOperationFactory, ProdOperationFormData
from tests.unit.route_tech.factories.prod_oper_pos import ProdOperationPosFormData

from route_tech.models import EconomicActivitySubject
from route_tech.errors import EASErrors, GWCErrors, ProdOperErrors, ProdOperationPosErrors
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
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)

        cls.main_subject = EconomicActivitySubject.objects.create(
            name="eas",
            short_name="eas",
            main_class=cls.enterprise,
            main_subject=None,
        )
        cls.daughter_subject = EconomicActivitySubject.objects.create(
            name="eas",
            short_name="eas",
            main_class=cls.enterprise,
            main_subject=cls.main_subject
        )
        cls.granddaughter_subject = EconomicActivitySubject.objects.create(
            name="eas",
            short_name="eas",
            main_class=cls.enterprise,
            main_subject=cls.daughter_subject,
        )

        cls.valid_data = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=None,
        )
        cls.update_data = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=cls.main_subject.pk,
        )
        cls.empty_name_data = EASFormData(
            name=None,
            main_class=cls.enterprise.pk,
        )
        cls.empty_short_name_data = EASFormData(
            short_name=None,
            main_class=cls.enterprise.pk,
        )
        cls.empty_main_class_data = EASFormData(
            main_class=None,
        )
        cls.empty_main_subject_data = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=None,
        )
        cls.valid_data_with_main_subject = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=cls.main_subject.pk,
        )

        cls.invalid_data_with_cycle_reference = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=cls.daughter_subject.pk
        )
        cls.invalid_data_with_cycle_self_reference = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=cls.main_subject.pk
        )
        cls.invalid_data_with_cycle_transitive_reference = EASFormData(
            main_class=cls.enterprise.pk,
            main_subject=cls.main_subject.pk
        )

    def test_main_class_queryset(self):
        form = EconomicActivitySubjectForm()
        queryset = form.fields["main_class"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(len(queryset), 3)

    def test_main_subject_queryset(self):
        form = EconomicActivitySubjectForm()
        queryset = form.fields["main_subject"].queryset
        self.assertIsInstance(queryset, QuerySet)
        self.assertEqual(len(queryset), 3)

    def test_name_field_is_required(self):
        form = EconomicActivitySubjectForm(self.empty_name_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"][0], EASErrors.EMPTY_NAME)

    def test_short_name_field_is_required(self):
        form = EconomicActivitySubjectForm(self.empty_short_name_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["short_name"][0], EASErrors.EMPTY_SHORT_NAME)

    def test_main_class_field_is_required(self):
        form = EconomicActivitySubjectForm(self.empty_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["main_class"][0], EASErrors.EMPTY_MAIN_CLASS)

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

    def test_cycle_reference_causes_internal_error_exception_to_be_raised(self):
        form = EconomicActivitySubjectForm(self.invalid_data_with_cycle_reference, instance=self.main_subject)
        self.assertFalse(form.is_valid())
        self.assertIn("main_subject", form.errors)
        self.assertEqual(
            form.errors["main_subject"],
            [EASErrors.CYCLE_DETECTED]
        )

    def test_cycle_self_reference_causes_internal_error_exception_to_be_raised(self):
        form = EconomicActivitySubjectForm(self.invalid_data_with_cycle_self_reference, instance=self.main_subject)
        self.assertFalse(form.is_valid())
        self.assertIn("main_subject", form.errors)
        self.assertEqual(
            form.errors["main_subject"],
            [EASErrors.CYCLE_DETECTED]
        )

    def test_cycle_transitive_reference_causes_internal_error_exception_to_be_raised(self):
        form = EconomicActivitySubjectForm(self.invalid_data_with_cycle_transitive_reference, instance=self.main_subject)
        self.assertFalse(form.is_valid())
        self.assertIn("main_subject", form.errors)
        self.assertEqual(
            form.errors["main_subject"],
            [EASErrors.CYCLE_DETECTED]
        )


class GroupWorkingCenterFormTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.enterprise = ClassStructFactory(
            name="Means of labor 1",
            short_name="MeansL1",
            main_class=cls.means_of_labor,
        )
        cls.department = ClassStructFactory(
            name="Department 1",
            short_name="Dept1",
            main_class=cls.means_of_labor,
        )
        cls.another_department = ClassStructFactory(
            name="Department 2",
            short_name="Dept2",
            main_class=cls.means_of_labor,
        )

        cls.eas1 = EASFactory(main_class=cls.enterprise)
        cls.eas2 = EASFactory(main_class=cls.enterprise, main_subject=cls.eas1)

        cls.place = 42

        cls.valid_data = GWCFormData(
            main_class=cls.enterprise.pk,
            eas=cls.eas1.pk,
            place=cls.place,
        )
        cls.update_data = GWCFormData(
            main_class=cls.department.pk,
            eas=cls.eas2.pk,
            place=cls.place + 10,
        )
        cls.empty_name_data = GWCFormData(
            name="",
            main_class=cls.enterprise.pk,
            eas=cls.eas1.pk,
            place=cls.place,
        )
        cls.empty_short_name_data = GWCFormData(
            short_name="",
            main_class=cls.enterprise.pk,
            eas=cls.eas1.pk,
            place=cls.place,
        )
        cls.empty_main_class_data = GWCFormData(
            main_class=None,
            eas=cls.eas1.pk,
            place=cls.place,
        )
        cls.empty_eas_data = GWCFormData(
            main_class=cls.enterprise.pk,
            eas=None,
            place=cls.place,
        )
        cls.empty_place_data = GWCFormData(
            main_class=cls.enterprise.pk,
            eas=cls.eas1.pk,
            place=None,
        )

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
        self.assertEqual(form.errors["name"][0], GWCErrors.EMPTY_NAME)

    def test_short_name_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_short_name_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["short_name"][0], GWCErrors.EMPTY_SHORT_NAME)

    def test_main_class_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_main_class_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["main_class"][0], GWCErrors.EMPTY_MAIN_CLASS)

    def test_eas_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_eas_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["eas"][0], GWCErrors.EMPTY_EAS)

    def test_place_field_is_required(self):
        form = GroupWorkingCenterForm(self.empty_place_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["place"][0], GWCErrors.EMPTY_PLACE)

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
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)

        cls.nuts_subclass = ClassStructFactory(
            name="Nuts subclass",
            short_name="nuts subcls",
            main_class=cls.nuts_class,
        )
        cls.stand = ClassStructFactory(
            name="Assembly stand",
            short_name="stand",
            main_class=cls.means_of_labor,
        )

        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.eas = EASFactory(main_class=cls.enterprise)
        cls.center = GWCFactory(
            main_class=cls.stand,
            eas=cls.eas,
            place=10,
        )
        cls.prod = ProdFactory(
            class_field=cls.nuts_subclass,
            image=None,
        )

        cls.num_of_workers = 3
        cls.t_pz = 1.5
        cls.t_sht = 2.5

        cls.valid_data = ProdOperationFormData(
            prod=cls.prod.pk,
            tech_oper=cls.tech_oper.pk,
            profession=cls.profession.pk,
            center=cls.center.pk,
            qualification=cls.qualification.pk,
            num_of_workers=cls.num_of_workers,
            t_pz=cls.t_pz,
            t_sht=cls.t_sht,
        )
        cls.update_data = ProdOperationFormData(
            prod=cls.prod.pk,
            tech_oper=cls.tech_oper.pk,
            profession=cls.profession.pk,
            center=cls.center.pk,
            qualification=cls.qualification.pk,
            num_of_workers=cls.num_of_workers + 1,
            t_pz=cls.t_pz + 0.5,
            t_sht=cls.t_sht + 0.5,
        )
        cls.empty_prod_data = ProdOperationFormData(
            prod=None, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=cls.num_of_workers, t_pz=cls.t_pz, t_sht=cls.t_sht,
        )
        cls.empty_tech_oper_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=None, profession=cls.profession.pk,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=cls.num_of_workers, t_pz=cls.t_pz, t_sht=cls.t_sht,
        )
        cls.empty_profession_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=None,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=cls.num_of_workers, t_pz=cls.t_pz, t_sht=cls.t_sht,
        )
        cls.empty_center_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=None, qualification=cls.qualification.pk,
            num_of_workers=cls.num_of_workers, t_pz=cls.t_pz, t_sht=cls.t_sht,
        )
        cls.empty_qualification_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=cls.center.pk, qualification=None,
            num_of_workers=cls.num_of_workers, t_pz=cls.t_pz, t_sht=cls.t_sht,
        )
        cls.empty_num_of_workers_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=None, t_pz=cls.t_pz, t_sht=cls.t_sht,
        )
        cls.empty_t_pz_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=cls.num_of_workers, t_pz=None, t_sht=cls.t_sht,
        )
        cls.empty_t_sht_data = ProdOperationFormData(
            prod=cls.prod.pk, tech_oper=cls.tech_oper.pk, profession=cls.profession.pk,
            center=cls.center.pk, qualification=cls.qualification.pk,
            num_of_workers=cls.num_of_workers, t_pz=cls.t_pz, t_sht=None,
        )

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
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)
        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)

        cls.nuts_subclass = ClassStructFactory(
            name="Nuts subclass",
            short_name="nuts subcls",
            main_class=cls.nuts_class,
        )
        cls.stand = ClassStructFactory(
            name="Assembly stand",
            short_name="stand",
            main_class=cls.means_of_labor,
        )

        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.eas = EASFactory(main_class=cls.enterprise)
        cls.center = GWCFactory(
            main_class=cls.stand,
            eas=cls.eas,
            place=10,
        )

        cls.prod_input = ProdFactory(class_field=cls.nuts_subclass, image=None)
        cls.prod_output = ProdFactory(class_field=cls.nuts_subclass, image=None)

        cls.input_prod_oper = ProdOperationFactory(
            prod=cls.prod_input,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=3,
            t_pz=1.0,
            t_sht=1.0,
        )
        cls.output_prod_oper = ProdOperationFactory(
            prod=cls.prod_output,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
            num_of_workers=3,
            t_pz=1.0,
            t_sht=1.0,
        )

        cls.input_quantity = Decimal("5.50")
        cls.output_quantity = Decimal("7.50")

        cls.valid_data = ProdOperationPosFormData(
            input_prod_oper=cls.input_prod_oper.pk,
            output_prod_oper=cls.output_prod_oper.pk,
            input_quantity=cls.input_quantity,
            output_quantity=cls.output_quantity,
        )
        cls.update_data = ProdOperationPosFormData(
            input_prod_oper=cls.input_prod_oper.pk,
            output_prod_oper=cls.output_prod_oper.pk,
            input_quantity=cls.input_quantity + Decimal("0.5"),
            output_quantity=cls.output_quantity + Decimal("0.5"),
        )
        cls.empty_input_prod_oper_data = ProdOperationPosFormData(
            input_prod_oper=None,
            output_prod_oper=cls.output_prod_oper.pk,
            input_quantity=cls.input_quantity,
            output_quantity=cls.output_quantity,
        )
        cls.empty_output_prod_oper_data = ProdOperationPosFormData(
            input_prod_oper=cls.input_prod_oper.pk,
            output_prod_oper=None,
            input_quantity=cls.input_quantity,
            output_quantity=cls.output_quantity,
        )
        cls.empty_input_quantity_data = ProdOperationPosFormData(
            input_prod_oper=cls.input_prod_oper.pk,
            output_prod_oper=cls.output_prod_oper.pk,
            input_quantity=None,
            output_quantity=cls.output_quantity,
        )
        cls.empty_output_quantity_data = ProdOperationPosFormData(
            input_prod_oper=cls.input_prod_oper.pk,
            output_prod_oper=cls.output_prod_oper.pk,
            input_quantity=cls.input_quantity,
            output_quantity=None,
        )
        cls.invalid_input_quantity_data = ProdOperationPosFormData(
            input_prod_oper=cls.input_prod_oper.pk,
            output_prod_oper=cls.output_prod_oper.pk,
            input_quantity=Decimal("-0.1"),
            output_quantity=cls.output_quantity,
        )
        cls.invalid_output_quantity_data = ProdOperationPosFormData(
            input_prod_oper=cls.input_prod_oper.pk,
            output_prod_oper=cls.output_prod_oper.pk,
            input_quantity=cls.input_quantity,
            output_quantity=Decimal("-0.1"),
        )

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
