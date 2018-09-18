from raceentries.models import RaceEntry
from runs.models import Run
from django.db.models import Q

def get_available_runs(race_entry, checkpoint):
    runs = Run.objects.filter(race_entry=race_entry).filter(Q(race_entry__entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(race_entry__entry_status=RaceEntry.ENTRY_STATUS_CUT)).filter(job__pick_checkpoint=checkpoint).filter(status=Run.RUN_STATUS_ASSIGNED)
    return runs