import factory
from faker import Factory

from django.utils import timezone

faker = Factory.create()


class SpecificationLogsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "specifications.SpecificationLogs"
    pair = None
    updated_at = factory.LazyFunction(lambda: timezone.now)
    old_quantity = factory.LazyFunction(lambda: faker.pydecimal(
        min_value=1,
        max_value=5,
        left_digits=1,
        right_digits=1,
    ))
    old_quantity = factory.LazyFunction(lambda: faker.pydecimal(
        min_value=6,
        max_value=9,
        left_digits=1,
        right_digits=1,
    ))


class SpecificationLogsFormData(factory.DictFactory):
    updated_at = factory.LazyFunction(lambda: timezone.now)
    old_quantity = factory.LazyFunction(lambda: faker.pydecimal(
        min_value=1,
        max_value=5,
        left_digits=1,
        right_digits=1,
    ))
    new_quantity = factory.LazyFunction(lambda: faker.pydecimal(
        min_value=6,
        max_value=9,
        left_digits=1,
        right_digits=1,
    ))
