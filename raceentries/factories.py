import factory
from .models import RaceEntry
from racers.factories import RacerFactory
from races.factories import RaceFactory

class RaceEntryFactory(factory.DjangoModelFactory):
    
    racer = RacerFactory()
    race = RaceFactory()

    entry_status = RaceEntry.ENTRY_STATUS_ENTERED

    class Meta:
        model = RaceEntry