from .models import Message
from runs.models import Run
from raceentries.models import RaceEntry
import datetime
import pytz

def get_next_message(race, dispatcher=None):
    right_now = datetime.datetime.now(tz=pytz.utc)
    if race.race_start_time > right_now:
        message = Message(message_type=Message.MESSAGE_TYPE_ERROR)
        return message
    message = Message.objects.filter(confirmed=False).filter(message_time__lte=right_now).first()
    #TODO .filter(dispatcher=dispatcher)
    
    if message:
        return message
    
    race_entries = RaceEntry.objects.filter(race=race)
    if race_entries:
        for race in race_entries:
            ##check for a clear racer
            pass
    
    runs = Run.objects.filter(race_entry__race=race).filter(race_entry__entry_status=RaceEntry.ENTRY_STATUS_RACING).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)

    if runs:
        race_entry = runs.first().race_entry
        runs_to_assign = Run.objects.filter(race_entry=race_entry).filter(status=Run.RUN_STATUS_PENDING).filter(utc_time_ready__lte=right_now)
        message = Message(race=race_entry.race, race_entry=race_entry)
        message.save()
        
        for run in runs_to_assign:
            message.runs.add(run)
            run.status = Run.RUN_STATUS_DISPATCHING
            run.save()
        message.save()
       
        return message
        #TODO set dispatcher. 