from django.db import models
from django.conf import settings

class Checkpoint(models.Model):

    checkpoint_number = models.IntegerField(unique=True)
    checkpoint_name = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return u"#{} {}".format(self.checkpoint_number, self.checkpoint_name)
    
    def get_absolute_url(self):
        return u"/checkpoints/details/" + str(self.id) + "/"