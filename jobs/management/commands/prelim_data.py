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
from time import sleep

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
        race = Race.objects.get(pk=2)
        right_now = datetime.datetime.now(tz=pytz.utc)
        NUMBER_OF_DISPATCHERS = 4
        
        #clean slate
        RaceEntry.objects.filter(race=race).delete()
        Message.objects.filter(race=race).delete()
                
        racers = Racer.objects.all()
        
        checkpoints = list(Checkpoint.objects.all())
        for checkpoint in checkpoints:
            checkpoint.value = 0
            
        for racer in racers:
            re = RaceEntry(racer=racer, race=race)
            re.save()
            
        while RaceEntry.objects.filter(Q(entry_status=RaceEntry.ENTRY_STATUS_ENTERED) | Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT)).exists():
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
                
                
            messages_this_minute = 0
            while messages_this_minute <= NUMBER_OF_DISPATCHERS:
                next_message = get_next_message(race)
                messages_this_minute += 1
                if not next_message.message_type == Message.MESSAGE_TYPE_NOTHING:
                    print next_message.pk, next_message
                    if random.random() > .7:
                        next_message.confirm()
                    else:
                        next_message.snooze()
                else:
                    break
                        
            run_messages_count = Run.objects.filter(utc_time_ready__lte=right_now).filter(status=Run.RUN_STATUS_PENDING).values_list('race_entry', flat=True).distinct().count()
            messages_count = Message.objects.filter(race=race).filter(status=Message.MESSAGE_STATUS_SNOOZED).filter(message_time__lte=right_now).count()
            print "messages we didn't get to rn ", run_messages_count + messages_count
            
            racing_entries = RaceEntry.objects.filter(Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT))
            for entry in racing_entries:
                if entry.last_action:
                    long_enough = datetime.timedelta(seconds=random.randint(180, 360)) / 60
                    if datetime.datetime.now(tz=pytz.utc) - entry.last_action > long_enough:
                        #they did something 3-6 minutes ago, let's simulate another action
                        
                        #are they clear and cut? 
                        runs = Run.objects.filter(race_entry=entry).filter(Q(status=Run.RUN_STATUS_PICKED) | Q(status=Run.RUN_STATUS_ASSIGNED))
                        if not runs:
                            if entry.entry_status == RaceEntry.ENTRY_STATUS_CUT:
                                if Message.objects.filter(race_entry=entry).filter(message_type=Message.MESSAGE_TYPE_OFFICE).filter(status=Message.MESSAGE_STATUS_CONFIRMED).exists():
                                    entry.finish_racer()
                                    print "{} finished".format(entry)
                        else:
                            runs = Run.objects.filter(race_entry=entry)
                            picks = runs.filter(status=Run.RUN_STATUS_ASSIGNED)
                            drops = runs.filter(status=Run.RUN_STATUS_PICKED)
                            if picks :
                                pick_checkpoints = picks.values_list('job__pick_checkpoint', flat=True).distinct()
                            else:
                                pick_checkpoints = []
                            if drops:
                                drop_checkpoints = drops.values_list('job__drop_checkpoint', flat=True).distinct()
                            else:
                                drop_checkpoints = []
                            try:    
                                checkpoint_list = list(Checkpoint.objects.filter(Q(pk__in=pick_checkpoints) | Q(pk__in=drop_checkpoints)).distinct())
                                current_checkpoint = random.choice(checkpoint_list)
                            except:
                                print "blip"
                                current_checkpoint = random.choice(checkpoints)
                            for run in picks.filter(job__pick_checkpoint=current_checkpoint):
                                run.pick()
                            for run in drops.filter(job__drop_checkpoint=current_checkpoint):
                                if random.random() >= .8:
                                    run.utc_time_due = right_now - datetime.timedelta(seconds=30)
                                    run.save()
                                run.drop()
                            entry.add_up_points()
                            entry.add_up_runs()
                            entry.save()
            
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
            sleep(1)
                
    print "race data created."