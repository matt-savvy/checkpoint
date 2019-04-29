import factory
from faker import Faker
from .models import Company
from nacccusers.factories import NACCCUserFactory

class CompanyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker('company')
    dispatcher = factory.SubFactory(NACCCUserFactory)
