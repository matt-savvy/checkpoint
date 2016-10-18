from django.core.management.base import BaseCommand, CommandError
from racers.models import Racer
from races.models import Race
from runs.models import Run
from racelogs.models import RaceEvent, RaceLog
from raceentries.models import RaceEntry
import decimal
import datetime

class Command(BaseCommand):
    RACE_MINUTES = 180
    def handle(self, *args, **options):
         RaceEvent.objects.all().delete()
         race = Race.objects.get(pk=args[0])
         
         re = RaceEntry.objects.filter(race=race)
         
         for current_minute in range(0, self.RACE_MINUTES + 1):
            print current_minute
            the_time = race.race_start_time + datetime.timedelta(minutes=current_minute)
            for entry in re:
                if entry.racer.racer_number == '997':
                    pass
                else:
                    if current_minute == 0:
                        event = RaceEvent()
                        event.minute = current_minute
                        event.racer = entry.racer
                        event.save()
                    elif current_minute == 180:
                        event = RaceEvent()
                        event.minute = current_minute
                        event.racer = entry.racer
                        event.points = entry.grand_total
                        event.save()
                    else:
                        event = RaceEvent()
                        log = RaceLog.objects.filter(race=race).filter(racer=entry.racer).filter(entered__lte=the_time).order_by('-entered').first()
                        event.minute = current_minute
                        event.racer = entry.racer
                        event.points = log.current_grand_total
                        event.save()
                    
            
            
        
                
        
    
    