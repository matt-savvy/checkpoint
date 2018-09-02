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
    
    class Meta:
        model = Checkpoint