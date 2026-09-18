import factory
from faker import Factory

from products.constants import ProdConsts

faker = Factory.create()


class ProdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "products.Prod"

    name = factory.LazyFunction(lambda: faker.first_name()[:ProdConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.first_name()[:ProdConsts.SHORT_NAME_MAX_LENGTH])
    class_field = None
    image = factory.django.ImageField(
        color='blue', width=800, height=600, filename='test_image.jpg'
    )
    cost = factory.LazyFunction(lambda: faker.pydecimal(min_value=1, max_value=100))
    modification = None
    ei = None


class ProdFormData(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:ProdConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.first_name()[:ProdConsts.SHORT_NAME_MAX_LENGTH])
    class_field = None
    image = None
    cost = factory.LazyFunction(lambda: faker.pydecimal(min_value=1, max_value=100, left_digits=3, right_digits=2))
    modification = None
    ei = None


class ModificationFormData(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:ProdConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.first_name()[:ProdConsts.SHORT_NAME_MAX_LENGTH])
