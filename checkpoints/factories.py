import factory
import random
from races.models import Race
from races.factories import RaceFactory
from checkpoints.models import Checkpoint
from faker import Faker
fake = Faker()

class CheckpointFactory(factory.DjangoModelFactory):
    checkpoint_number = factory.Sequence(lambda n: "%d" % n)
    checkpoint_name = factory.Faker('company')
    address_line_1 = factory.Faker('street_address')
    address_line_2 = factory.Faker('secondary_address')

    class Meta:
        model = Checkpoint
