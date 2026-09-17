import factory
from faker import Factory

faker = Factory.create()


class ParClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "classes.ParClass"

    class_field = None
    parametr = None
    num = None
    min_value = factory.LazyFunction(lambda: faker.pyfloat(min_value=1, max_value=10))
    max_value = factory.LazyFunction(lambda: faker.pyfloat(min_value=11, max_value=20))


class ParClassFormData(factory.DictFactory):
    class_field = None
    parametr = None
    min_value = factory.LazyFunction(lambda: faker.pyfloat(min_value=1, max_value=10))
    max_value = factory.LazyFunction(lambda: faker.pyfloat(min_value=11, max_value=20))


class ChangeParClassFormData(factory.DictFactory):
    cls_1 = None
    cls_2 = None
