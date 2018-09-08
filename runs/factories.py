import factory
from runs.models import Run
from raceentries.factories import RaceEntryFactory
from jobs.factories import JobFactory

class RunFactory(factory.DjangoModelFactory):

    job = factory.SubFactory(JobFactory)
    race_entry = factory.SubFactory(RaceEntryFactory)
    status = Run.RUN_STATUS_PENDING

    class Meta:
        model = Run