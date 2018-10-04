from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
from dispatch.models import Message
from runs.models import Run
from racers.models import Racer
from raceentries.models import RaceEntry
from checkpoints.models import Checkpoint
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
        races = Race.objects.order_by('pk')
        for race in races:
            print "{} {}".format(race.pk, race)
        #selection_race = int(raw_input("choose race number : "))
       
        #race = Race.objects.get(pk=selection_race)
        race = Race.objects.get(pk=1)
        right_now = datetime.datetime.now(tz=pytz.utc)
        race.race_start_time = right_now
        race.race_start_time = race.race_start_time.replace(second=0, microsecond=0)
        race.save()
        #clean slate
        RaceEntry.objects.filter(race=race).delete()
        Message.objects.filter(race=race).delete()
        #pdb.set_trace()
        if Racer.objects.filter(gender=Racer.GENDER_MALE).count() < 65:
            difference = 65 - Racer.objects.filter(gender=GENDER_MALE).count()
            RacerFactory.create_batch(difference, gender=GENDER_MALE)
    
        if Racer.objects.exclude(gender=Racer.GENDER_MALE).count() < 15:
            difference = 65 - Racer.objects.exclude(gender=GENDER_MALE).count()
            RacerFactory.create_batch(difference, gender=GENDER_FEMALE)
           
        racers_men = Racer.objects.filter(gender=Racer.GENDER_MALE).all()[:65]
        racers_wtf = Racer.objects.exclude(gender=Racer.GENDER_MALE).all()[:15]
        starting_position = 2
        for racer in racers_wtf:
            racer.starting_position = starting_position
            racer.save()
            starting_position += 2
            
        starting_position = 1
        for racer in racers_men:
            racer.starting_position = starting_position
            racer.save()
            starting_position += 2
        
        racers_working_men = Racer.objects.filter(gender=Racer.GENDER_MALE).filter(category=Racer.RACER_CATEGORY_MESSENGER).all()[:20]
        racers_working_wtf = Racer.objects.exclude(gender=Racer.GENDER_MALE).filter(category=Racer.RACER_CATEGORY_MESSENGER).all()[:5]
        racers = list(racers_men) + list(racers_wtf) + list(racers_working_men) + list(racers_working_wtf)
        racers = set(racers)
        
        
        speed = 12
        NUMBER_OF_DISPATCHERS = 3
        checkpoints = Checkpoint.objects.all()
        for racer in racers:
            entry = RaceEntry(racer=racer, race=race, entry_status=RaceEntry.ENTRY_STATUS_ENTERED)
            entry.starting_position = racer.starting_position
            entry.save()
            race.populate_runs(entry)
            entry.start_racer()
        
        finish_time_delta = datetime.timedelta(minutes=race.time_limit) / speed
        print "go"
        right_now = datetime.datetime.now(tz=pytz.utc)
        print "right now, ", right_now
        while right_now <= race.race_start_time + finish_time_delta + datetime.timedelta(minutes=10):
            
            simulate_race(race, NUMBER_OF_DISPATCHERS, checkpoints, speed)

            if not RaceEntry.objects.filter(race=race).filter(Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT)).exists():
                break

        print "race data created."
        