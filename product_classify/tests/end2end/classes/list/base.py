from django.urls import reverse

from faker import Faker

from classes.constants import ProductsConsts, ClassStructConsts
from classes.models import ClassStruct

from tests.end2end.components.pages.classes.list import ClassesListPage
from tests.end2end.base import EndToEndTest


class ClassesEmptyListBaseEndToEndTest(EndToEndTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.prod_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        cls.url = cls.server_url + reverse("classes:category_classes", args=[cls.prod_class.pk])
        cls.page.goto(cls.url)

        cls.list_page = ClassesListPage(cls.page)


class ClassesFilledListBaseEndToEndTest(EndToEndTest):
    def setUp(self):
        super().setUp()
        faker = Faker()
        self.prod_class = ClassStruct.objects.get(pk=ProductsConsts.NUTS_ID)
        self.child_prod_class1 = ClassStruct.objects.create(
            name=faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=self.prod_class
        )
        self.child_prod_class2 = ClassStruct.objects.create(
            name=faker.name()[:ClassStructConsts.NAME_MAX_LENGTH],
            short_name=faker.name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH],
            base_ei=None,
            main_class=self.prod_class
        )
        self.url = self.live_server_url + reverse("classes:category_classes", args=[self.prod_class.pk])
        self.page.goto(self.url)
        self.list_page = ClassesListPage(self.page)
