import factory
from .models import CompanyEntry
from companies.factories import CompanyFactory
from races.factories import RaceFactory

class CompanyEntryFactory(factory.DjangoModelFactory):
    class Meta:
        model = CompanyEntry

    race = factory.SubFactory(RaceFactory)
    company = factory.SubFactory(CompanyFactory)
