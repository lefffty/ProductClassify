from django.test import TestCase


class BaseUnitTestCase(TestCase):
    fixtures = [
        "ei.json",
        "classes.json",
    ]
