from django.db import models
from racers.models import Racer
from races.models import Race

class StreamEvent(models.Model):
    """(StreamEvent description)"""
    race = models.ForeignKey(Race)
    timestamp = models.DateTimeField(auto_now_add=True)
    racer = models.ForeignKey(Racer)
    message = models.CharField(max_length=255, blank=True)
    message_photo = models.CharField(max_length=255, blank=True)
    poster_name = models.CharField(max_length=100, blank=True)
    poster_photo = models.CharField(max_length=255, blank=True)
    published = models.BooleanField(default=False)
    
    class Admin:
        list_display = ('race', 'timestamp', 'racer', 'message', 'poster_name', 'published')

    def __unicode__(self):
        return u"StreamEvent"
