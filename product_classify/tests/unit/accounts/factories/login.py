import factory
from faker import Factory

from accounts.constants import UserConsts

faker = Factory.create()


class LoginFormData(factory.DictFactory):
    email = factory.LazyFunction(lambda: faker.email()[:UserConsts.EMAIL_MAX_LENGTH])
    password = factory.LazyFunction(lambda: faker.password()[:UserConsts.PASSWORD_MAX_LENGTH])
