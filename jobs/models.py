from django.db import models
from races.models import Race, Manifest
from checkpoints.models import Checkpoint
import datetime

class Job(models.Model):
    
    """(Job description)"""
    job_id = models.IntegerField(unique=True)
    race = models.ForeignKey(Race)
    pick_checkpoint = models.ForeignKey(Checkpoint, related_name="pick")
    drop_checkpoint = models.ForeignKey(Checkpoint, related_name="drop")
    points = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    minutes_ready_after_start = models.IntegerField(default=0)
    minutes_due_after_start = models.IntegerField(default=9999)
    manifest = models.ForeignKey(Manifest, blank=True, null=True)
    
    def __unicode__(self):
        return u"#{} {} to {}".format(str(self.id), self.pick_checkpoint, self.drop_checkpoint)
    
    def get_absolute_url(self):
        return "/jobs/details/" + str(self.id) + "/"
    
    @property
    def abosolute_ready_time(self):
        if self.race.race_start_time:
            return self.race.race_start_time + datetime.timedelta(minutes=self.minutes_ready_after_start)