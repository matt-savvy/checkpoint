import factory
import random
from races.models import Race, Manifest
from checkpoints.models import Checkpoint
from faker import Faker
import random
fake = Faker()

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

def get_color_name():
    """return random color name that's not taken"""
    used_colors = Manifest.objects.values_list('manifest_name', flat=True)
    color = fake.color_name()
    while color in used_colors:
        color = fake.color_name()
    return color

class ManifestFactory(factory.DjangoModelFactory):
    race = factory.SubFactory(RaceFactory)
    manifest_name = factory.LazyFunction(get_color_name)
    manifest_type = Manifest.TYPE_CHOICE_STARTING
    
    class Meta:
        model = Manifest