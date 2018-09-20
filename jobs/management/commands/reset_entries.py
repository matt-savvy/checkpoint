from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
from racecontrol.models import RaceControl
from checkpoints.models import Checkpoint
from raceentries.models import RaceEntry
from runs.models import Run
from dispatch.models import Message
from racelogs.models import RaceLog, RaceEvent
import random
import itertools

class Command(BaseCommand):   
   def handle(self, *args, **options):
       #races = Race.objects.order_by('pk')
       #for race in races:
       #     print "{} {}".format(race.pk, race)
       #selection_race = int(raw_input("choose race number : "))
       #selection_number_of_jobs = int(raw_input("number of jobs: "))
       #
       #race = Race.objects.get(pk=selection_race)
       current_race = RaceControl.shared_instance().current_race
       entries = RaceEntry.objects.filter(race=current_race)
       for entry in entries:
           entry.entry_status = RaceEntry.ENTRY_STATUS_ENTERED
           entry.save()
           
       runs = Run.objects.filter(race_entry__in=entries).delete()
       messages = Message.objects.filter(race=current_race).delete()
       racelogs = RaceLog.objects.filter(race=current_race).delete()
       print "race reset"