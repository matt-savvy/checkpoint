import factory
from .models import Message
from races.factories import RaceFactory
from runs.factories import RunFactory
from jobs.factories import JobFactory
from raceentries.factories import RaceEntryFactory

def generate_jobs():
    import random
    number_of_jobs = random.randint(1, 5)
    jobs = JobFactory.create_batch(number_of_jobs)
    
    return jobs

class MessageFactory(factory.DjangoModelFactory):
    race = factory.SubFactory(RaceFactory)
    race_entry =  factory.SubFactory(RaceEntryFactory)
    runs = factory.RelatedFactory(RunFactory)
    #message_time = models.DateTimeField(blank=True, null=True)
    #message_type = models.IntegerField(choices=MESSAGE_TYPE_CHOICES, default=MESSAGE_TYPE_DISPATCH)
    
    class Meta:
        model = Message