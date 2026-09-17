import factory
from faker import Factory


faker = Factory.create()


class ParProdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "products.ParProd"

    prod = None
    par = None
    int_value = None
    double_value = None
    enum_val = None
