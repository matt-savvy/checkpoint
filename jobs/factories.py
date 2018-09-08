import factory
import random
from jobs.models import Job
from races.factories import RaceFactory
from checkpoints.factories import CheckpointFactory
from faker import Faker

def get_job_id():
    last_job = Job.objects.order_by('job_id').last()
    if last_job:
        last_job_id = last_job.job_id
        return int(last_job_id) + 1
    else:
        return 1
        
class JobFactory(factory.DjangoModelFactory):
    """(Job description)"""
    job_id = factory.Sequence(lambda n: "%d" % n)
    race = factory.SubFactory(RaceFactory)
    pick_checkpoint = factory.SubFactory(CheckpointFactory)
    drop_checkpoint = factory.SubFactory(CheckpointFactory)
    points = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    minutes_ready_after_start = 0
    minutes_due_after_start = 9999
    
    class Meta:
        model = Job