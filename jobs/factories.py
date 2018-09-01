import factory
import random
from jobs.models import Job
from races.factories import RaceFactory
from checkpoints.factories import CheckpointFactory
from faker import Faker

class JobFactory(factory.DjangoModelFactory):
    
    """(Job description)"""
    job_id = factory.Sequence(lambda n: '%d' % n)
    race = RaceFactory()
    pick_checkpoint = CheckpointFactory()
    drop_checkpoint = CheckpointFactory()
    points = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    minutes_ready_after_start = 0
    minutes_due_after_start = 9999
    
    class Meta:
        model = Job