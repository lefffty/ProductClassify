from django.utils import timezone

import factory
from faker import Factory

from accounts.constants import UserConsts

faker = Factory.create()


def generate_phone_number():
    return faker.numerify("+7 (###) ###-##-##")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.User"

    email = factory.LazyFunction(lambda: faker.email()[:UserConsts.EMAIL_MAX_LENGTH])
    first_name = factory.LazyFunction(lambda: faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH])
    middle_name = factory.LazyFunction(lambda: faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH])
    last_name = factory.LazyFunction(lambda: faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH])
    phone_number = factory.LazyFunction(generate_phone_number)
    role = None
    date_joined = factory.LazyFunction(timezone.now)
    is_staff = False
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "StrongPass123!"
        self.set_password(password)
        if create:
            self.save()


class UserFormData(factory.DictFactory):
    email = factory.LazyFunction(lambda: faker.email()[:UserConsts.EMAIL_MAX_LENGTH])
    first_name = factory.LazyFunction(lambda: faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH])
    middle_name = factory.LazyFunction(lambda: faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH])
    last_name = factory.LazyFunction(lambda: faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH])
    phone_number = factory.LazyFunction(generate_phone_number)
