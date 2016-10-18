from django.core.management.base import BaseCommand, CommandError
from racers.models import Racer
from races.models import Race
from runs.models import Run
from raceentries.models import RaceEntry
import decimal

class Command(BaseCommand):
    
   def handle(self, *args, **options):
        race = Race.objects.get(pk=args[0])
        race_entries = RaceEntry.objects.filter(race=race)
        runs = Run.objects.filter(job__race=race)
        
        for the_run in runs:
            if the_run.determination == Run.DETERMINATION_NOT_DROPPED:
                the_run.points_awarded = decimal.Decimal(-the_run.job.points)
                the_run.save()
        
        for race_entry in race_entries:
            race_entry.add_up_points()
            race_entry.save()
            
        
                
        
    
    