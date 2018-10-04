from .models import Message
from runs.models import Run
from raceentries.models import RaceEntry
from races.models import Race, Manifest
from jobs.models import Job
from django.db.models import Q
import datetime
import pytz
import random 
from checkpoints.models import Checkpoint 
from time import sleep

def snooze_capped_runs(race_entry):
    runs = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING)
    if race_entry.race.overtime:
        minutes_to_snooze = 5
        runs = runs.filter(job__manifest__manifest_type=Manifest.TYPE_CHOICE_BONUS)
    else:
        minutes_to_snooze = 15
        runs = runs.exclude(job__manifest__manifest_type=Manifest.TYPE_CHOICE_BONUS)
        
    for run in runs:
        run.utc_time_ready += datetime.timedelta(minutes=minutes_to_snooze)
        run.save()
        
def assign_runs(runs_to_assign, race_entry):    
    right_now = datetime.datetime.now(tz=pytz.utc)
    runs_to_snooze = False
    message = Message(race=race_entry.race, race_entry=race_entry, message_type=Message.MESSAGE_TYPE_DISPATCH, status=Message.MESSAGE_STATUS_DISPATCHING, message_time=right_now)
    message.save()
    
    current_count = run_count(race_entry)
    if current_count + runs_to_assign.count() > race_entry.race.run_limit:
                
        difference = race_entry.race.run_limit - current_count
        runs_to_assign = runs_to_assign[:difference]
        runs_to_snooze = True
        
    for run in runs_to_assign:
        message.runs.add(run)
        run.status = Run.RUN_STATUS_DISPATCHING    
        run.utc_time_assigned = right_now
        run.save()
    
    if runs_to_snooze:
        snooze_capped_runs(race_entry)
    
    message.save()

    #TODO assign dispatcher to message
    return message

def run_count(race_entry):
    current_run_count = Run.objects.filter(race_entry=race_entry).filter(Q(status=Run.RUN_STATUS_ASSIGNED) | Q(status=Run.RUN_STATUS_PICKED)).count()
    return current_run_count
    
def get_next_message(race, dispatcher=None):
    right_now = datetime.datetime.now(tz=pytz.utc)
    overtime_manifest = Manifest.objects.filter(race=race).filter(manifest_type=Manifest.TYPE_CHOICE_BONUS).first()
    
    if race.race_end_time:
        if race.race_end_time <= right_now:
            race_entries = RaceEntry.objects.filter(Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT)).filter(race=race).order_by('start_time', 'starting_position')
            for entry in race_entries:
                office_messages = Message.objects.filter(race_entry=entry).filter(message_type=Message.MESSAGE_TYPE_OFFICE).exists()
                if not office_messages:
                    message = Message(race=race, race_entry=entry, message_type=Message.MESSAGE_TYPE_OFFICE, status=Message.MESSAGE_STATUS_DISPATCHING)
                    message.save()
                    return message
            
    #if we're at the five minute warning, so any messages we were going to "Get back to" are wiped
    if race.five_minute_warning:
        Message.objects.filter(status=Message.MESSAGE_STATUS_SNOOZED).filter(message_type=Message.MESSAGE_TYPE_DISPATCH).filter(race_entry__race=race).delete()
        Message.objects.filter(Q(status=Message.MESSAGE_STATUS_DISPATCHING) | Q(status=Message.MESSAGE_STATUS_NONE)).filter(race_entry__race=race).filter(message_time__lte=right_now - datetime.timedelta(minutes=3)).delete()
    

    
    ## are there any SNOOZED messages IN THIS RACE that already exist?
    snoozed_messages = Message.objects.filter(status=Message.MESSAGE_STATUS_SNOOZED).filter(race_entry__race=race).filter(message_time__lte=right_now)
    if snoozed_messages:
        snoozed_message = snoozed_messages.first()
        print "found snoozed message"
        snoozed_message.status = Message.MESSAGE_STATUS_DISPATCHING
        snoozed_message.save()
        return snoozed_message
    ## are there any messages marked DISPATCHING IN THIS RACE that are older than three minutes? maybe someone closed the tab and now it's in purgatory
    
    old_unconfirmed_messages = Message.objects.filter(Q(status=Message.MESSAGE_STATUS_DISPATCHING) | Q(status=Message.MESSAGE_STATUS_NONE)).filter(race_entry__race=race).filter(message_time__lte=right_now - datetime.timedelta(minutes=3))
    if old_unconfirmed_messages:
        print "found unconfirmed"
        return old_unconfirmed_messages.first()
    
    ##are there any clear racers? they get top priority
    race_entry = race.find_clear_racer()

    if race_entry:
        print "found clear racer"
        office_messages = Message.objects.filter(race_entry=race_entry).filter(message_type=Message.MESSAGE_TYPE_OFFICE).exists()
        
        #if they're cut, we'll tell them unless we already tried
        if race_entry.entry_status == RaceEntry.ENTRY_STATUS_CUT:
            if not office_messages:
                message = Message(race=race, race_entry=race_entry, message_type=Message.MESSAGE_TYPE_OFFICE, status=Message.MESSAGE_STATUS_DISPATCHING)
                message.save()
                return message
        
        ##if they're racing but the time limit is in five minutes or less, they are gonna get cut
        elif race_entry.five_minute_warning:
            print "five_minute_warning"
            race_entry.cut_racer()
            message = Message(race=race, race_entry=race_entry, message_type=Message.MESSAGE_TYPE_OFFICE, status=Message.MESSAGE_STATUS_DISPATCHING)
            message.save()
            
            return message
            
        runs = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING)
        if race.overtime:
            runs = runs.filter(job__manifest=overtime_manifest)
        elif not race.overtime and overtime_manifest:
            runs = runs.exclude(job__manifest=overtime_manifest)
        
        if runs:
            #any runs with no ready time for whatver reason will get treated as if they are ready now
            runs_with_no_ready_time = runs.filter(utc_time_ready=None)
            if runs_with_no_ready_time:
                runs_to_assign = runs_with_no_ready_time
            else:
                #grab the next run and any runs that are ready at the same time
                next_run_ready_time = runs.first().utc_time_ready
                runs_to_assign = runs.filter(utc_time_ready__lte=next_run_ready_time)
  
            return assign_runs(runs_to_assign, race_entry)
        else:
            if not office_messages:
                message = Message(race=race, race_entry=race_entry, message_type=Message.MESSAGE_TYPE_OFFICE, status=Message.MESSAGE_STATUS_DISPATCHING)
                message.save()
                return message

    runs = Run.objects.filter(race_entry__race=race).filter(race_entry__entry_status=RaceEntry.ENTRY_STATUS_RACING).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)
    
    ##we don't want to filter it down to jobs with no manifest otherwise racers with an assigned manifest get no work
    if race.overtime and overtime_manifest:
        runs = runs.filter(job__manifest=overtime_manifest)
        
    elif not race.overtime and overtime_manifest:
        runs = runs.exclude(job__manifest=overtime_manifest)
    
    while runs.all().exists():
        race_entry = runs.first().race_entry
        
        if race_entry.race_end_time <= right_now:
            office_messages = Message.objects.filter(race_entry=race_entry).filter(message_type=Message.MESSAGE_TYPE_OFFICE).exists()
            if not office_messages:
                message = Message(race=race, race_entry=race_entry, message_type=Message.MESSAGE_TYPE_OFFICE, status=Message.MESSAGE_STATUS_DISPATCHING)
                message.save()
                return message
        
        runs_to_assign = runs.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)

        if run_count(race_entry) < race_entry.race.run_limit:
            return assign_runs(runs_to_assign, race_entry)
        else:
            snooze_capped_runs(race_entry)
            
    message = Message(race=race, message_type=Message.MESSAGE_TYPE_NOTHING)
    message.save()
    return message
    
def simulate_race(race, NUMBER_OF_DISPATCHERS, checkpoints, speed=60):
    right_now = datetime.datetime.now(tz=pytz.utc)
    messages_this_minute = 0
    racing_entries = RaceEntry.objects.filter(race=race).filter(Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT))
    
    while messages_this_minute <= NUMBER_OF_DISPATCHERS:
        next_message = get_next_message(race)
        messages_this_minute += 1
        if not next_message.message_type == Message.MESSAGE_TYPE_NOTHING:
            print next_message.race_entry.starting_position, next_message
            if random.random() < .7:
                next_message.confirm()
            else:
                next_message.snooze()
        else:
            break
    
    
    run_messages_count = Run.objects.filter(race_entry__race=race).filter(utc_time_ready__lte=right_now).filter(status=Run.RUN_STATUS_PENDING).values_list('race_entry', flat=True).distinct().count()
    messages_count = Message.objects.filter(race=race).filter(status=Message.MESSAGE_STATUS_SNOOZED).filter(message_time__lte=right_now).count()
    
    clear_rider_count = 0
        
    for entry in racing_entries.all():
        ##CLEAR RIDER COUNT MATH##
        run_count = Run.objects.filter(race_entry=entry).filter(Q(status=Run.RUN_STATUS_ASSIGNED) | Q(status=Run.RUN_STATUS_PICKED) | Q(status=Run.RUN_STATUS_DISPATCHING)).count()
        if run_count == 0:
            current_message = Message.objects.filter(race_entry=entry).filter(status=Message.MESSAGE_STATUS_DISPATCHING).exists()
            already_confirmed_cut = Message.objects.filter(race_entry=entry).filter(message_type=Message.MESSAGE_TYPE_OFFICE).filter(Q(status=Message.MESSAGE_STATUS_CONFIRMED) | Q(status=Message.MESSAGE_STATUS_SNOOZED)).exists()
            if not current_message and not already_confirmed_cut:
                clear_rider_count += 1
        ## END CLEAR
        
        if entry.last_action:
            long_enough = datetime.timedelta(seconds=random.randint(180, 360)) / speed
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
    
    print "messages we didn't get to rn ", run_messages_count + messages_count
    print "clear riders ", clear_rider_count
    print "\n"
    
    sleep(60 / speed)
    
    
    return checkpoints