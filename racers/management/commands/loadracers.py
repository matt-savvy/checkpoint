from django.core.management.base import BaseCommand, CommandError
from racers.models import Racer
import sys, os
import csv


class Command(BaseCommand):
    
   def handle(self, *args, **options):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        
        with open(os.path.join(__location__, 'racers.csv'), 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                try:
                    racer = Racer.objects.get(racer_number=row[5])
                except:
                    r = Racer()
                    r.racer_number = row[5]
                    r.first_name = row[1]
                    r.last_name = row[3]
                    r.nick_name = row[2]
                    r.city = row[4]
                    r.gender = row[8]
                    r.team = row[6]
                
                    if row[7] == 'CIVILIAN':
                        r.category = Racer.RACER_CATEGORY_NON_MESSENGER
                    elif row[7] == 'MESSENGER':
                        r.category = Racer.RACER_CATEGORY_MESSENGER
                    elif row[7] == 'RETIRED MESSENGER':
                        r.category = Racer.RACER_CATEGORY_EX_MESSENGER
                    else:
                        r.category = Racer.RACER_CATEGORY_ERIN_YOUNG
                    
                    r.save()
                
        
    
    