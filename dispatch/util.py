from .models import Message
from runs.models import Run
from raceentries.models import RaceEntry
import datetime
import pytz

def assign_runs(runs_to_assign, race_entry):
    message = Message(race=race_entry.race, race_entry=race_entry)
    message.save()
    
    for run in runs_to_assign:
        message.runs.add(run)
        run.status = Run.RUN_STATUS_DISPATCHING
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
    message = Message.objects.filter(confirmed=False).filter(message_time__lte=right_now).first()
    
    if message:
        return message
    
    race_entry = race.find_clear_racer()
    if race_entry:
        runs = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING)
        if runs:
            next_run_ready_time = runs.first().utc_time_ready
            runs_to_assign = runs.filter(utc_time_ready__lte=next_run_ready_time)
            for run in runs_to_assign:
                run.utc_time_ready = right_now
                run.save()
                #TODO log this
            return assign_runs(runs_to_assign, race_entry)
    
    runs = Run.objects.filter(race_entry__race=race).filter(race_entry__entry_status=RaceEntry.ENTRY_STATUS_RACING).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)

    if runs:
        race_entry = runs.first().race_entry
        runs_to_assign = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)
        return assign_runs(runs_to_assign, race_entry)
    
    message = Message(message_type=Message.MESSAGE_TYPE_NOTHING)
    return message
        