from checkpoints.models import Checkpoint
from racers.models import Racer
from raceentries.models import RaceEntry
from jobs.models import Job
from runs.models import Run

def get_available_runs(race_entry, checkpoint):
    runs = Run.objects.filter(race_entry=race_entry).filter(job__pick_checkpoint=checkpoint).filter(status=Run.RUN_STATUS_ASSIGNED)
    return runs