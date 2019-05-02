from django.db import models
from django.conf import settings

class Checkpoint(models.Model):

    checkpoint_number = models.IntegerField(unique=True)
    checkpoint_name = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=144, blank=True, null=True)
    address_line_2 = models.CharField(max_length=144, blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['checkpoint_number']

    def __unicode__(self):
        return u"({}){}".format(self.checkpoint_number, self.checkpoint_name)

    def get_absolute_url(self):
        return u"/checkpoints/details/" + str(self.id) + "/"
