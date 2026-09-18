import factory
from faker import Factory

from route_tech.constants import GWCConsts

faker = Factory.create()


class GWCFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "route_tech.GroupWorkingCenter"

    name = factory.LazyFunction(lambda: faker.first_name()[:GWCConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.last_name()[:GWCConsts.SHORT_NAME_MAX_LENGTH])
    main_class = None
    eas = None
    place = factory.LazyFunction(lambda: faker.pyint())


class GWCFormData(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:GWCConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.last_name()[:GWCConsts.SHORT_NAME_MAX_LENGTH])
    main_class = None
    eas = None
    place = factory.LazyFunction(lambda: faker.pyint())
