import factory
from faker import Factory


faker = Factory.create()


class ProdComponentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "specifications.ProdComponent"
    parent_prod = None
    component = None
    num = None
    quantity = factory.LazyFunction(lambda: faker.pydecimal(left_digits=1, right_digits=1))


class ProdComponentFormData(factory.DictFactory):
    parent_prod = None
    component = None
    quantity = factory.LazyFunction(lambda: faker.pydecimal(left_digits=1, right_digits=1))
