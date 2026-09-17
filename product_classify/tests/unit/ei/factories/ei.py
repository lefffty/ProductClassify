import factory
from faker import Factory

from ei.constants import EiConsts

faker = Factory.create()


class EiFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "ei.Ei"

    name = factory.LazyFunction(lambda: faker.first_name()[:EiConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.first_name()[:EiConsts.SHORT_NAME_MAX_LENGTH])
    code = factory.LazyFunction(lambda: faker.ean()[:EiConsts.CODE_MAX_LENGTH])
    convert_factor = factory.LazyFunction(lambda: faker.pyfloat(min_value=0, max_value=100)) 
    main_class = None


class ChildEiFactory(EiFactory):
    main_class = factory.SubFactory(EiFactory)


class EiFormDataFactory(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:EiConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.first_name()[:EiConsts.SHORT_NAME_MAX_LENGTH])
    code = factory.LazyFunction(lambda: faker.ean()[:EiConsts.CODE_MAX_LENGTH])
    convert_factor = factory.LazyFunction(lambda: faker.pyfloat(min_value=0, max_value=100)) 
    main_class = None
