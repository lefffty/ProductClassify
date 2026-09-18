import factory
from faker import Factory

from parametr.constants import ParametrConsts

faker = Factory.create()


class ParametrFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "parametr.Parametr"

    name = factory.LazyFunction(lambda: faker.first_name()[:ParametrConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.last_name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH])
    parametr_type = None
    par_ei = None


class ParametrFormData(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:ParametrConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.last_name()[:ParametrConsts.SHORT_NAME_MAX_LENGTH])
    parametr_type = None
    par_ei = None
