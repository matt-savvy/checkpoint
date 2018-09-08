import factory
import random
from races.models import Race, Manifest
from checkpoints.models import Checkpoint
from faker import Faker
import random

def get_random_race_tpye():
    "Return a random category from available choices."
    lt_choices = [x[0] for x in Race.RACE_TYPE_CHOICES]
    return random.choice(lt_choices)

class RaceFactory(factory.DjangoModelFactory):
    race_name = factory.Faker('word')
    race_type = factory.LazyFunction(get_random_race_tpye)
    time_limit = factory.Faker('pyint')
    race_start_time = factory.Faker('past_datetime', start_date='-1d', tzinfo=None)
    
    class Meta:
        model = Race

def get_random_manifest_type():
    "Return a random category from available choices."
    lt_choices = [x[0] for x in Manifest.TYPE_CHOICES]
    return random.choice(lt_choices)

class ManifestFactory(factory.DjangoModelFactory):
    race = factory.SubFactory(RaceFactory)
    manifest_name = factory.Faker('color_name')
    order = factory.Sequence(lambda n : "%d" % n)
    manifest_type = Manifest.TYPE_CHOICE_MAIN
    
    class Meta:
        model = Manifest