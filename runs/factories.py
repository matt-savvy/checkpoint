import factory
from runs.models import Run
from raceentries.factories import RaceEntryFactory
from jobs.factories import JobFactory

class RunFactory(factory.DjangoModelFactory):

    job = JobFactory()
    race_entry = RaceEntryFactory()
    status = Run.RUN_STATUS_ASSIGNED

    class Meta:
        model = Run