from django.db import models
from racers.models import Racer
from races.models import Race
from nacccusers.models import NACCCUser

class RaceLog(models.Model):
    entered = models.DateTimeField(auto_now_add=True)
    racer = models.ForeignKey(Racer)
    race = models.ForeignKey(Race)
    user = models.ForeignKey(NACCCUser, blank=True, null=True)
    log = models.CharField(max_length=255)
    current_grand_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    current_number_of_runs = models.IntegerField(default=0)

class RaceEvent(models.Model):
    minute = models.IntegerField()
    racer = models.ForeignKey(Racer)
    points = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    