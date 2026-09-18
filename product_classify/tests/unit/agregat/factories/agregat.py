import factory
from faker import Factory

faker = Factory.create()


class AgregatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "agregat.Agregat"
        
    agr = None
    par = None
    num = 1
