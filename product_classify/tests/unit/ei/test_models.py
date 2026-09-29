from tests.unit.base import BaseUnitTestCase
from tests.unit.ei.factories.ei import EiFactory, ChildEiFactory

from ei.models import Ei


class EiModelTest(BaseUnitTestCase):
    def test_string_representation(self):
        short_name = "short_"
        ei = EiFactory(short_name=short_name)
        self.assertEqual(str(ei), short_name)

    def test_create_with_minimal_requirements(self):
        ei = EiFactory()
        self.assertIsNotNone(ei.pk)
        self.assertIsNotNone(ei.name)
        self.assertIsNotNone(ei.short_name)
        self.assertIsNotNone(ei.code)
        self.assertIsNotNone(ei.convert_factor)
        self.assertIsNone(ei.main_class)

    def test_convert_factor_accepts_integer(self):
        convert_factor = 1
        ei = EiFactory(convert_factor=1)
        self.assertEqual(ei.convert_factor, convert_factor)

    def test_convert_factor_accepts_float(self):
        convert_factor = 1.0
        ei = EiFactory(convert_factor=1.0)
        self.assertEqual(ei.convert_factor, convert_factor)

    def test_main_class_relation(self):
        parent = EiFactory()
        child = ChildEiFactory(main_class=parent)
        self.assertEqual(child.main_class, parent)
        self.assertIn(child, parent.child_eis.all())

    def test_main_class_reassignment_is_correct(self):
        ei1 = EiFactory()
        ei2 = ChildEiFactory(main_class=ei1)
        ei3 = ChildEiFactory(main_class=ei2)

        ei1.delete()
        ei2.refresh_from_db()
        ei3.refresh_from_db()
        self.assertNotEqual(ei2.main_class, ei1)
        self.assertIsNone(ei2.main_class)
        self.assertEqual(ei3.main_class, ei2)


class MainClassIdChangeOnEiDeleteTriggerTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        # удаляемая единица измерения не имеет дочерних элементов
        cls.gr1_ei1 = EiFactory()
        # удаляемая единица измерения имеет один дочерний элемент
        cls.gr2_ei1 = EiFactory()
        cls.gr2_ei2 = ChildEiFactory(main_class=cls.gr2_ei1)
        # удаляемая единица измерения имеет несколько дочерних элементов
        cls.gr3_ei1 = EiFactory()
        cls.gr3_ei2 = ChildEiFactory(main_class=cls.gr3_ei1)
        cls.gr3_ei3 = ChildEiFactory(main_class=cls.gr3_ei1)

    def test_removable_object_does_not_have_children(self):
        removable_pk = self.gr1_ei1.pk

        self.gr1_ei1.delete()

        self.assertEqual(Ei.objects.filter(main_class_id=removable_pk).count(), 0)

    def test_removable_object_has_one_child(self):
        removable_pk = self.gr2_ei1.pk
        new_main_class_id = self.gr2_ei2.pk
        
        self.gr2_ei1.delete()

        self.assertEqual(Ei.objects.filter(main_class_id=removable_pk).count(), 0)
        self.assertEqual(Ei.objects.filter(main_class_id=new_main_class_id).count(), 0)

    def test_removable_object_has_more_than_one_children(self):
        removable_pk = self.gr3_ei1.pk
        new_main_class_id = self.gr3_ei2.pk

        self.gr3_ei1.delete()

        self.assertEqual(Ei.objects.filter(main_class_id=removable_pk).count(), 0)
        self.assertEqual(Ei.objects.filter(main_class_id=new_main_class_id).count(), 1)

    def test_removable_object_is_not_parent(self):
        main_class_id = self.gr3_ei3.main_class_id

        self.gr3_ei3.delete()

        self.assertEqual(Ei.objects.filter(main_class_id=main_class_id).count(), 1)
