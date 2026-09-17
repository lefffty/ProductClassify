import factory
from faker import Factory

from classes.constants import ClassStructConsts, ProdClassConsts, EnumClassConsts

faker = Factory.create()


class ClassStructFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "classes.ClassStruct"

    name = factory.LazyFunction(lambda: faker.first_name()[:ClassStructConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.last_name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH])
    base_ei = None
    main_class = None


class ChildClassStructFactory(ClassStructFactory):
    main_class = factory.SubFactory(ClassStructFactory)


class ProdClassFormData(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:ProdClassConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.first_name()[:ProdClassConsts.SHORT_NAME_MAX_LENGTH])
    base_ei = None
    main_class = None


class EnumsClassFormData(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:EnumClassConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.first_name()[:EnumClassConsts.SHORT_NAME_MAX_LENGTH])
    main_class = None


class ClassFormData(factory.DictFactory):
    name = factory.LazyFunction(lambda: faker.first_name()[:ClassStructConsts.NAME_MAX_LENGTH])
    short_name = factory.LazyFunction(lambda: faker.first_name()[:ClassStructConsts.SHORT_NAME_MAX_LENGTH])
    main_class = None
