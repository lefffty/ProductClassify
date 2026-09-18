import factory
from faker import Factory

from route_tech.constants import EASConsts

faker = Factory.create()


class EASFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "route_tech.EconomicActivitySubject"

    name = factory.LazyFunction(lambda: faker.first_name()[:EASConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.last_name()[:EASConsts.SHORT_NAME_MAX_LENGTH])
    main_class = None
    main_subject = None


class EASFormData(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:EASConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.last_name()[:EASConsts.SHORT_NAME_MAX_LENGTH])
    main_class = None
    main_subject = None
