import factory
from faker import Factory

faker = Factory.create()


class ProdOperationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "route_tech.ProdOperation"

    prod = None
    tech_oper = None
    profession = None
    center = None
    qualification = None
    num_of_workers = factory.LazyFunction(lambda: faker.pyint(min_value=1, max_value=100))
    t_pz = factory.LazyFunction(lambda: faker.pyfloat())
    t_sht = factory.LazyFunction(lambda: faker.pyfloat())


class ProdOperationFormData(factory.DictFactory):
    prod = None
    tech_oper = None
    profession = None
    center = None
    qualification = None
    num_of_workers = factory.LazyFunction(lambda: faker.pyint(min_value=1, max_value=100))
    t_pz = factory.LazyFunction(lambda: faker.pyfloat())
    t_sht = factory.LazyFunction(lambda: faker.pyfloat())
