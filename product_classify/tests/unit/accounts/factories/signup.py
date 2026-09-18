import factory
from faker import Factory

from accounts.constants import UserConsts
from tests.unit.accounts.factories.user import generate_phone_number

faker = Factory.create()


class SignUpFormData(factory.DictFactory):
    email = factory.LazyFunction(lambda: faker.email()[:UserConsts.EMAIL_MAX_LENGTH])
    first_name = factory.LazyFunction(lambda: faker.first_name()[:UserConsts.FIRST_NAME_MAX_LENGTH])
    middle_name = factory.LazyFunction(lambda: faker.first_name()[:UserConsts.MIDDLE_NAME_MAX_LENGTH])
    last_name = factory.LazyFunction(lambda: faker.last_name()[:UserConsts.LAST_NAME_MAX_LENGTH])
    phone_number = factory.LazyFunction(generate_phone_number)
    password1 = factory.LazyFunction(lambda: faker.password()[:UserConsts.PASSWORD_MAX_LENGTH])
    password2 = factory.LazyAttribute(lambda o: o.password1)
    role = None
