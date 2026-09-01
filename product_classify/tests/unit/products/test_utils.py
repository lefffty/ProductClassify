from faker import Faker

from tests.unit.base import BaseUnitTestCase

from classes.models import ClassStruct, ParClass
from ei.models import Ei
from products.models import Prod, ParProd
from products.utils import get_filtered_products
from parametr.models import Parametr
from enums.models import Enums
from classes.constants import ProdClassConsts, ProductsConsts, ParamIds, EnumsIds


class GetFilteredProductsTest(BaseUnitTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()

        cls.base_ei = Ei.objects.first()

        cls.nuts_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.int_par_type = ClassStruct.objects.get(pk=ParamIds.INT)
        cls.int_enum_type = ClassStruct.objects.get(pk=EnumsIds.INT)

        cls.nuts_subclass = ClassStruct.objects.create(
            name=cls.faker.name()[:ProdClassConsts.NAME_MAX_LENGTH],
            short_name=cls.faker.name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH],
            main_class=cls.nuts_class,
            base_ei=cls.base_ei
        )
        cls.enum_subclass = ClassStruct.objects.create(
            name="enum class",
            short_name="class",
            main_class=cls.int_enum_type,
            base_ei=cls.base_ei,
        )

        cls.prod1 = Prod.objects.create(
            name="test prod1",
            short_name="prod1",
            class_field=cls.nuts_subclass,
            image=None,
            cost=200,
            modification=None,
            ei=cls.base_ei
        )
        cls.prod2 = Prod.objects.create(
            name="test prod2",
            short_name="prod2",
            class_field=cls.nuts_subclass,
            image=None,
            cost=200,
            modification=None,
            ei=cls.base_ei
        )

        cls.par1_name = "test parametr1"
        cls.par2_name = "test parametr2"

        cls.par1 = Parametr.objects.create(
            name=cls.par1_name,
            short_name="parametr1",
            parametr_type=cls.int_par_type,
            par_ei=cls.base_ei,
        )
        cls.par2 = Parametr.objects.create(
            name=cls.par2_name,
            short_name="parametr2",
            parametr_type=cls.int_enum_type,
            par_ei=cls.base_ei,
        )

        cls.enum1 = Enums.objects.create(
            enum=cls.enum_subclass,
            num=1,
            name=None,
            short_name=None,
            double_value=None,
            int_value=2,
            image=None,
        )
        cls.enum2 = Enums.objects.create(
            enum=cls.enum_subclass,
            num=2,
            name=None,
            short_name=None,
            double_value=None,
            int_value=4,
            image=None,
        )

        cls.parclass1 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par1,
            num=1,
            min_value=100,
            max_value=200
        )
        cls.parclass2 = ParClass.objects.create(
            class_field=cls.nuts_subclass,
            parametr=cls.par2,
            num=2,
            min_value=None,
            max_value=None
        )

        cls.parprod1_1 = ParProd.objects.create(
            prod=cls.prod1,
            par=cls.par1,
            int_value=150,
            double_value=None,
            enum_val=None,
        )
        cls.parprod1_2 = ParProd.objects.create(
            prod=cls.prod1,
            par=cls.par2,
            int_value=None,
            double_value=None,
            enum_val=cls.enum1,
        )

        cls.parprod2_1 = ParProd.objects.create(
            prod=cls.prod2,
            par=cls.par1,
            int_value=120,
            double_value=None,
            enum_val=None,
        )
        cls.parprod2_2 = ParProd.objects.create(
            prod=cls.prod2,
            par=cls.par2,
            int_value=None,
            double_value=None,
            enum_val=cls.enum2,
        )
        cls.products_qs = Prod.objects.filter(class_field=cls.nuts_subclass)

    def test_filtered_products_returns_all_products_if_filters_were_not_specified(self):
        filtered_queryset = get_filtered_products(self.products_qs, {}, self.nuts_subclass.pk)
        self.assertEqual(list(filtered_queryset), [self.prod1, self.prod2])

    def test_filtered_products_returns_not_none_queryset_if_products_fits_filters(self):
        param_name = self.parclass1.parametr.name
        filtered_queryset = get_filtered_products(
            self.products_qs,
            {
                param_name: ("140", "160")
            },
            self.nuts_subclass.pk
        )
        self.assertEqual(list(filtered_queryset), [self.prod1])

    def test_filtered_products_returns_none_queryset_if_products_does_not_fit_filters(self):
        param_name = self.parclass1.parametr.name
        filtered_queryset = get_filtered_products(
            self.products_qs,
            {
                param_name: ("180", "190"),
            },
            self.nuts_subclass.pk
        )
        self.assertEqual(list(filtered_queryset), [])
