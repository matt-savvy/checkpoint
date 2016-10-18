from django.db import models
from races.models import Race

class RaceControl(models.Model):
    current_race = models.ForeignKey(Race, blank=True, null=True)
    racers_started = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(pk=self.pk).delete()
        super(RaceControl, self).save(*args, **kwargs)
    
    @classmethod
    def shared_instance(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()
