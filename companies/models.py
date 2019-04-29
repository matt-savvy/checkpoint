from django.db import models
from nacccusers.models import NACCCUser

class Company(models.Model):
    name = models.CharField(max_length=255)
    dispatcher = models.ForeignKey(NACCCUser)

    def __unicode__(self):
        return self.name

    def get_racers(self):
        from racers.models import Racer
        return Racer.objects.filter(company=self)
