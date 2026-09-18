import factory
from faker import Factory

from enums.constants import EnumsConsts

faker = Factory.create()


class EnumsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "enums.Enums"

    enum = None
    num = None
    name = factory.LazyFunction(lambda: faker.first_name()[:EnumsConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.last_name()[:EnumsConsts.SHORT_NAME_MAX_LENGTH])
    double_value = None
    int_value = None
    image = None


class EnumsFormData(factory.DictFactory):
    enum = None
    name = None
    short_name = None
    double_value = None
    int_value = None
    image = None


class ChangeNumFormData(factory.DictFactory):
    enum_1 = None
    enum_2 = None
