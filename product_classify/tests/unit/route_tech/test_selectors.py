from classes.constants import MetaConsts
from classes.models import ClassStruct

from route_tech.selectors import EASSelector

from tests.unit.base import BaseUnitTestCase
from tests.unit.route_tech.factories.eas import EASFactory


class EASSelectorTestCase(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)

        cls.root = EASFactory(main_class=cls.enterprise)
        cls.first_root_child = EASFactory(
            main_class=cls.enterprise,
            main_subject=cls.root
        )
        cls.second_root_child = EASFactory(
            main_class=cls.enterprise,
            main_subject=cls.root
        )
        cls.first_root_grandchild = EASFactory(
            main_class=cls.enterprise,
            main_subject=cls.first_root_child
        )

    def test_get_all_eas_descendants(self):
        expected_ids = [
            self.first_root_child.pk,
            self.second_root_child.pk,
            self.first_root_grandchild.pk,
        ]

        actual_result = EASSelector.get_all_eas_descendants(self.root.pk)
        actual_ids = [record.id for record in actual_result]

        self.assertEqual(expected_ids, actual_ids)

    def test_records_has_correct_level_values(self):
        expected_level_values = [
            1,
            1,
            2
        ]

        actual_result = EASSelector.get_all_eas_descendants(self.root.pk)
        actual_level_values = [record.level for record in actual_result]

        self.assertEqual(expected_level_values, actual_level_values)

    def test_get_all_eas_descendants_is_empty(self):
        actual_result = EASSelector.get_all_eas_descendants(self.first_root_grandchild.pk)
        self.assertEqual(len(actual_result), 0)
