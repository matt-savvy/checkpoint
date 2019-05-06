from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
from dispatch.models import Message
from runs.models import Run
from racers.factories import RacerFactory
from company_entries.factories import CompanyEntryFactory
from racers.models import Racer
from raceentries.models import RaceEntry
from checkpoints.models import Checkpoint
from racecontrol.model import RaceControl
from django.db.models import Q
import decimal
import random
import itertools
import datetime
import pytz
import pdb
from dispatch.util import simulate_race
from freezegun import freeze_time

def random_permutation(iterable, r=2):
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))

class Command(BaseCommand):
    def handle(self, *args, **options):
#        races = Race.objects.order_by('pk')
#        for race in races:
#           print "{} {}".format(race.pk, race)
        #selection_race = int(raw_input("choose race number : "))

        #race = Race.objects.get(pk=selection_race)
        rc = RaceControl.shared_instance()
        race = rc.current_race
        right_now = datetime.datetime.now(tz=pytz.utc)
        race.race_start_time = right_now
        race.race_start_time = race.race_start_time.replace(second=0, microsecond=0)
        race.time_limit = 150
        race.save()
        #clean slate
        CompanyEntry.objects.filter(race=race).delete()
        CompanyEntryFactory.create_batch(8, race=race)
        for company_entry in CompanyEntry.objects.filter(race=race):
            RaceEntryFactory.create_batch(2, racer__company=company_entry.company, race=race, entry_status=RaceEntry.ENTRY_STATUS_ENTERED)

        speed = 12
        checkpoints = Checkpoint.objects.all()

        race.populate_runs(entry)

        finish_time_delta = datetime.timedelta(minutes=race.time_limit) / speed
        print "go"
        right_now = datetime.datetime.now(tz=pytz.utc)
        print "right now, ", right_now

            simulate_race(race, checkpoints, speed)

            if not RaceEntry.objects.filter(race=race).filter(entry_status=RaceEntry.ENTRY_STATUS_RACING).exists():
                break

        print "race data created."
