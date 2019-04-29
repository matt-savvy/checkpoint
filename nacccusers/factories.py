import factory
from .models import NACCCUser

class NACCCUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = NACCCUser

    username = factory.Faker('user_name')
