from .models import Message
from runs.models import Run
from raceentries.models import RaceEntry
import datetime
import pytz

def assign_runs(runs_to_assign, race_entry):
    message = Message(race=race_entry.race, race_entry=race_entry)
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
    right_now = datetime.datetime.now(tz=pytz.utc)
    if race.race_start_time > right_now:
        message = Message(message_type=Message.MESSAGE_TYPE_ERROR)
        return message
    
    #TODO .filter(dispatcher=dispatcher)
    ## are there any messages that already exist? snoozed ones, perhaps
    message = Message.objects.filter(confirmed=False).filter(message_time__lte=right_now).first()
    
    if message:
        return message
    
    ##are there any clear racers? they get top priority
    race_entry = race.find_clear_racer()
    if race_entry:
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
            #TODO
            ##do the time check
            ##assign jobs from the bonus manifest
            pass
            
    runs = Run.objects.filter(race_entry__race=race).filter(race_entry__entry_status=RaceEntry.ENTRY_STATUS_RACING).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)
    
    if runs:
        race_entry = runs.first().race_entry
        runs_to_assign = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)
        return assign_runs(runs_to_assign, race_entry)
    
    message = Message(race=race, message_type=Message.MESSAGE_TYPE_NOTHING)
    return message
        