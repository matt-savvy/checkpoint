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
from dispatch.util import get_next_message
from dispatch.models import Message
from dispatch.util import simulate_race

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
        selection_race = int(raw_input("choose race number : "))
       
        race = Race.objects.get(pk=selection_race)
        #race = Race.objects.get(pk=2)
        right_now = datetime.datetime.now(tz=pytz.utc)
        NUMBER_OF_DISPATCHERS = 4
        
        #clean slate
        RaceEntry.objects.filter(race=race).delete()
        Message.objects.filter(race=race).delete()
                
        racers = Racer.objects.all()
        
        checkpoints = list(Checkpoint.objects.all())
        for checkpoint in checkpoints:
            checkpoint.value = 0
            
        manifests = list(Manifest.objects.filter(race=race).exclude(manifest_type=Manifest.TYPE_CHOICE_BONUS))
        manifest_count = len(manifests)
        
        for x, racer in enumerate(racers):
            re = RaceEntry(racer=racer, race=race)
            if manifests:
                re.manifest = manifests[x % manifest_count]
                print re.manifest
            re.save()
            
        while RaceEntry.objects.filter(race=race).filter(Q(entry_status=RaceEntry.ENTRY_STATUS_ENTERED) | Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT)).exists():
            new_entry = RaceEntry.objects.filter(entry_status=RaceEntry.ENTRY_STATUS_ENTERED).first()
            if new_entry:
                new_entry.start_racer()
                print new_entry.racer, "start"
                right_now = datetime.datetime.now(tz=pytz.utc)
                runs = Run.objects.filter(race_entry=new_entry).filter(utc_time_ready__lte=right_now)
                
                message = Message(race_entry=new_entry, race=race, message_type=Message.MESSAGE_TYPE_DISPATCH, status=Message.MESSAGE_STATUS_DISPATCHING, message_time=right_now)
                message.save()
                for run in runs:
                    message.runs.add(run)
                    run.status = Run.RUN_STATUS_DISPATCHING    
                    run.utc_time_ready = right_now
                    run.save()
                message.save()
                message.confirm()
                
                
            checkpoints = simulate_race(race, NUMBER_OF_DISPATCHERS, checkpoints, 60)
                
            for checkpoint in checkpoints:
                new_value = Run.objects.filter(race_entry__race=race).filter(status=Run.RUN_STATUS_COMPLETED).filter(job__drop_checkpoint=checkpoint).count() - Run.objects.filter(race_entry__race=race).filter(status=Run.RUN_STATUS_PICKED).filter(job__pick_checkpoint=checkpoint).count() 
                if checkpoint.value:
                    if new_value < checkpoint.value:
                        checkpoint.value = new_value
                else:
                    checkpoint.value = new_value
                #print checkpoint,
                #print checkpoint.value
            print " "    
                
    print "race data created."