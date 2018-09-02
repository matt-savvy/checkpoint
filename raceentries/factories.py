import factory
from .models import RaceEntry
from racers.factories import RacerFactory
from races.factories import RaceFactory

class RaceEntryFactory(factory.DjangoModelFactory):
    
    racer = factory.SubFactory(RacerFactory)
    race = factory.SubFactory(RaceFactory)
    starting_position = factory.Sequence(lambda n: "%d" % n)
    entry_status = RaceEntry.ENTRY_STATUS_ENTERED

    class Meta:
        model = RaceEntry