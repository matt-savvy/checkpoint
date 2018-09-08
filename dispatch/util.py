from .models import Message
from runs.models import Run
from raceentries.models import RaceEntry
from races.models import Race, Manifest
from jobs.models import Job
from django.db.models import Q
import datetime
import pytz

def assign_runs(runs_to_assign, race_entry):
    message = Message(race=race_entry.race, race_entry=race_entry, message_type=Message.MESSAGE_TYPE_DISPATCH)
    message.save()
    right_now = datetime.datetime.now(tz=pytz.utc)
    
    for run in runs_to_assign:
        message.runs.add(run)
        run.status = Run.RUN_STATUS_DISPATCHING    
        run.utc_time_ready = right_now
        run.save()
    message.save()
    
    #TODO assign dispatcher to message
    return message

def get_next_message(race, dispatcher=None):
    if race.race_type != Race.RACE_TYPE_DISPATCH:
        message = Message(race=race, message_type=Message.MESSAGE_TYPE_ERROR)
        message.save()
        return message
    
    right_now = datetime.datetime.now(tz=pytz.utc)
    if race.race_start_time > right_now:
        message = Message(race=race, message_type=Message.MESSAGE_TYPE_ERROR)
        message.save()
        return message
    
    #TODO .filter(dispatcher=dispatcher)
    
    ## are there any SNOOZED messages IN THIS RACE that already exist?
    snoozed_messages = Message.objects.filter(status=Message.MESSAGE_STATUS_SNOOZED).filter(race_entry__race=race).filter(message_time__lte=right_now)
    if snoozed_messages.first():
        return snoozed_messages.first()
    ## are there any messages marked DISPATCHING IN THIS RACE that are older than two minutes? maybe someone closed the tab and now it's in purgatory
    
    old_unconfirmed_messages = Message.objects.filter(Q(status=Message.MESSAGE_STATUS_DISPATCHING) | Q(status=Message.MESSAGE_STATUS_NONE)).filter(race_entry__race=race).filter(message_time__lte=right_now - datetime.timedelta(minutes=2))
    if old_unconfirmed_messages.first():
        return old_unconfirmed_messages.first()
        
        
    ##are there any clear racers? they get top priority
    race_entry = race.find_clear_racer()

    if race_entry:
        if race_entry.entry_status == RaceEntry.ENTRY_STATUS_CUT:
            #if they're clear AND cut, we send them a cut message right away
            message = Message(race=race, race_entry=race_entry, message_type=Message.MESSAGE_TYPE_OFFICE)
            message.save()
            return message
            
        runs = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING)
        if runs:
            #any runs with no ready time for whatver reason will get treated as if they are ready now
            runs_with_no_ready_time = runs.filter(utc_time_ready=None)
            if runs_with_no_ready_time:
                runs_to_assign = runs_with_no_ready_time
            else:
                #grab the last run and any runs that are ready at the same time OR EARLIER
                next_run_ready_time = runs.last().utc_time_ready
                runs_to_assign = runs.filter(utc_time_ready__lte=next_run_ready_time)
  
            return assign_runs(runs_to_assign, race_entry)
        else:
            #see if there are any jobs on the bonus manifest that they haven't already done
            import pdb
            manifest = Manifest.objects.filter(race=race).filter(manifest_type=Manifest.TYPE_CHOICE_BONUS).first()
            if manifest:
                runs_done_by_racer = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_COMPLETED).filter(job__manifest=manifest)
                if right_now <= race.race_start_time + datetime.timedelta(minutes=manifest.cut_off_minutes_after_start):
                    bonus_jobs = Job.objects.filter(race=race, manifest=manifest).exclude(run__in=runs_done_by_racer)
                    if bonus_jobs:
                        bonus_jobs_to_assign = bonus_jobs[:3]
                        runs_to_assign = []
                        for job in bonus_jobs_to_assign:
                            run_to_assign = Run(job=job, race_entry=race_entry, status=Run.RUN_STATUS_PENDING)
                            run_to_assign.utc_time_ready = right_now
                            run_to_assign.save()
                            runs_to_assign.append(run_to_assign)
                            return assign_runs(runs_to_assign, race_entry)
            
            message = Message(race=race, race_entry=race_entry, message_type=Message.MESSAGE_TYPE_OFFICE)
            message.save()
            race_entry.cut_racer()
            return message
            #there is no bonus manifest, the bonus manifest has no jobs that racer hasn't done, or it is after the bonus manifest cut off
            #so we cut the rider
                
            
    runs = Run.objects.filter(race_entry__race=race).filter(race_entry__entry_status=RaceEntry.ENTRY_STATUS_RACING).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)
    
    if runs:
        race_entry = runs.first().race_entry
        runs_to_assign = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)
        return assign_runs(runs_to_assign, race_entry)
    
    message = Message(race=race, message_type=Message.MESSAGE_TYPE_NOTHING)
    message.save()
    return message
        