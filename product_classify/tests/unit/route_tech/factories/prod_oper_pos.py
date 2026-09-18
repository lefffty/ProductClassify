import factory
from faker import Factory

faker = Factory.create()


class ProdOperationPosFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "route_tech.ProdOperationPos"

    input_prod_oper = None
    output_prod_oper = None
    input_quantity = factory.LazyFunction(lambda: faker.pyfloat(left_digits=2, right_digits=1))
    output_quantity = factory.LazyFunction(lambda: faker.pyfloat(left_digits=2, right_digits=1))


class ProdOperationPosFormData(factory.DictFactory):
    input_prod_oper = None
    output_prod_oper = None
    input_quantity = factory.LazyFunction(lambda: faker.pyfloat(left_digits=2, right_digits=1))
    output_quantity = factory.LazyFunction(lambda: faker.pyfloat(left_digits=2, right_digits=1))
