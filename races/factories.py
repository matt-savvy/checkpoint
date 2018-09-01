import factory
import random
from races.models import Race
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