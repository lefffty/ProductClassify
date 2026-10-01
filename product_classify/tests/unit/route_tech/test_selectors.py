from decimal import Decimal

from classes.constants import (
    MetaConsts,
    OperationConsts,
    ProfessionConsts,
    QualificationConsts,
    ProductsConsts
)
from classes.models import ClassStruct

from ei.models import Ei

from route_tech.selectors import EASSelector
from route_tech.selectors import TechRouteSelector

from tests.unit.base import BaseUnitTestCase
from tests.unit.route_tech.factories.eas import EASFactory
from tests.unit.route_tech.factories.gwc import GWCFactory
from tests.unit.route_tech.factories.prod_oper import ProdOperationFactory
from tests.unit.route_tech.factories.prod_oper_pos import ProdOperationPosFactory
from tests.unit.products.factories.product import ProdFactory
from tests.unit.classes.factories.class_struct import ClassStructFactory


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


class TechRouteSelectorTestCase(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.tech_oper = ClassStruct.objects.get(pk=OperationConsts.WELDING)
        cls.profession = ClassStruct.objects.get(pk=ProfessionConsts.WELDER)
        cls.qualification = ClassStruct.objects.get(pk=QualificationConsts.FIRST_RANK)

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.product_class = ClassStructFactory(main_class=cls.nuts_class)

        cls.ei = Ei.objects.first()

        cls.prod = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("100.00"), ei=cls.ei,
        )
        cls.output_prod = ProdFactory(
            class_field=cls.product_class, image=None,
            cost=Decimal("200.00"), ei=cls.ei,
        )

        cls.enterprise = ClassStruct.objects.get(pk=MetaConsts.ENTERPRISE)
        cls.means_of_labor = ClassStruct.objects.get(pk=MetaConsts.MEANS_OF_LABOR)

        cls.stand = ClassStructFactory(main_class=cls.means_of_labor)
        cls.eas = EASFactory(main_class=cls.enterprise)
        cls.center = GWCFactory(main_class=cls.stand, eas=cls.eas, place=42)

        cls.parent_prod_oper = ProdOperationFactory(
            prod=cls.prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
        )
        cls.output_prod_oper1 = ProdOperationFactory(
            prod=cls.output_prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
        )
        cls.output_prod_oper2 = ProdOperationFactory(
            prod=cls.output_prod,
            tech_oper=cls.tech_oper,
            profession=cls.profession,
            center=cls.center,
            qualification=cls.qualification,
        )

        cls.existing_pos1 = ProdOperationPosFactory(
            input_prod_oper=cls.parent_prod_oper,
            output_prod_oper=cls.output_prod_oper1,
            input_quantity=Decimal("1.5"),
            output_quantity=Decimal("2.0"),
        )
        cls.existing_pos2 = ProdOperationPosFactory(
            input_prod_oper=cls.parent_prod_oper,
            output_prod_oper=cls.output_prod_oper2,
            input_quantity=Decimal("3.0"),
            output_quantity=Decimal("4.0"),
        )

        cls.product_id = cls.output_prod.pk

    def test_tech_route_function(self):
        tech_route = TechRouteSelector.get_tech_route(self.product_id)
        self.assertEqual(len(tech_route), 2)
