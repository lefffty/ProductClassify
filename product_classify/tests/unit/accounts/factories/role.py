import factory
from faker import Factory

from accounts.constants import RoleConsts

faker = Factory.create()


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.Role"

    code = factory.LazyFunction(lambda: faker.slug())
    name = factory.LazyFunction(lambda: faker.first_name()[:RoleConsts.NAME_MAX_LENGTH])
    description = factory.LazyFunction(lambda: faker.text())
    group = None
    is_self_registerable = False


class RoleFormData(factory.DictFactory):
    code = factory.LazyFunction(lambda: faker.slug())
    name = factory.LazyFunction(lambda: faker.first_name()[:RoleConsts.NAME_MAX_LENGTH])
    description = factory.LazyFunction(lambda: faker.text())
    group = None
    is_self_registrable = False
