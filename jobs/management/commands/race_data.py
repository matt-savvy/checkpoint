from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
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
        race.race_start_time = right_now - datetime.timedelta(minutes=75)
        race.race_start_time = race.race_start_time.replace(second=0, microsecond=0)
        race.save()
        #clean slate
        RaceEntry.objects.filter(race=race).delete()
       
        #pdb.set_trace()
        if Racer.objects.filter(gender=Racer.GENDER_MALE).count() < 65:
            difference = 65 - Racer.objects.filter(gender=GENDER_MALE).count()
            RacerFactory.create_batch(difference, gender=GENDER_MALE)
    
        if Racer.objects.exclude(gender=Racer.GENDER_MALE).count() < 15:
            difference = 65 - Racer.objects.exclude(gender=GENDER_MALE).count()
            RacerFactory.create_batch(difference, gender=GENDER_FEMALE)
           
        racers_men = Racer.objects.filter(gender=Racer.GENDER_MALE).all()[:65]
        racers_wtf = Racer.objects.exclude(gender=Racer.GENDER_MALE).all()[:15]
        racers_working_men = Racer.objects.filter(gender=Racer.GENDER_MALE).filter(category=Racer.RACER_CATEGORY_MESSENGER).all()[:20]
        racers_working_wtf = Racer.objects.exclude(gender=Racer.GENDER_MALE).filter(category=Racer.RACER_CATEGORY_MESSENGER).all()[:5]
        racers = list(racers_men) + list(racers_wtf) + list(racers_working_men) + list(racers_working_wtf)
        racers = set(racers)
        print "right now, ", right_now
        
        for racer in racers:
            #pdb.set_trace()
            print racer, 
            entry = RaceEntry(racer=racer, race=race, entry_status=RaceEntry.ENTRY_STATUS_ENTERED)
            entry.save()
            race.populate_runs(entry)
            entry.start_racer()
           
            runs = Run.objects.filter(race_entry=entry).filter(utc_time_ready__lte=right_now)
            current_time = race.race_start_time.replace(tzinfo=pytz.utc)
           
            while current_time <= right_now:
                random_minutes = datetime.timedelta(minutes=random.randint(5,14))
                current_time += random_minutes
                available_runs = runs.filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=current_time)
                for run in available_runs:
                    if Run.objects.filter(Q(status=Run.RUN_STATUS_PICKED) | Q(status=Run.RUN_STATUS_ASSIGNED)).filter(race_entry=entry).count() >= 13:
                        break
                    run.status = Run.RUN_STATUS_DISPATCHING
                    run.assign()                   
                    run.utc_time_assigned = current_time
                    run.utc_time_due = current_time + datetime.timedelta(minutes=run.job.minutes_due_after_start)
               
                    #70% chance that if they picked it up, a random time from now
                    if random.random() <= .7:
                        random_minutes = datetime.timedelta(seconds=random.randint(300,900))
                        pick_time = current_time + random_minutes
                        if pick_time <= right_now:
                            run.pick()
                            run.utc_time_picked = pick_time
                            run.save()
                       
                            #70% chance that if they picked it up, they're going to drop it
                            if random.random() <= .7:
                                random_minutes = datetime.timedelta(seconds=random.randint(180,1200))
                                drop_time = pick_time + random_minutes
                                if drop_time <= right_now:
                                    run.drop()
                                    run.utc_time_dropped = drop_time
                                    if run.utc_time_dropped <= run.utc_time_due:
                                        run.determination = Run.DETERMINATION_OK
                                        run.points_awarded = run.job.points
                                    else:
                                        run.determination = Run.DETERMINATION_LATE
                                        run.points_awarded = decimal.Decimal('0.00')
                                    run.save()
                   
            their_runs = Run.objects.filter(race_entry=entry)              
            print " picked {}, dropped {}.".format(their_runs.filter(status=Run.RUN_STATUS_PICKED).count(), their_runs.filter(status=Run.RUN_STATUS_COMPLETED).count())
    print "race data created."