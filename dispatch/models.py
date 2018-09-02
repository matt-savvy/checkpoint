from django.db import models
from races.models import Race
from raceentries.models import RaceEntry
from jobs.models import Job

class Message(models.Model):
    MESSAGE_TYPE_DISPATCH = 1
    MESSAGE_TYPE_OFFICE   = 2
    
    MESSAGE_TYPE_CHOICES = (
        (MESSAGE_TYPE_DISPATCH, 'Dispatching Jobs'),
        (MESSAGE_TYPE_OFFICE, 'Come to the Office'),
    )
    
    race = models.ForeignKey(Race)
    race_entry = models.ForeignKey(RaceEntry)
    jobs = models.ManyToManyField(Job)
    message_time = models.DateTimeField(blank=True, null=True)
    message_type = models.IntegerField(choices=MESSAGE_TYPE_CHOICES, default=MESSAGE_TYPE_DISPATCH)
    confirmed = models.BooleanField(default=False)
    confirmed_time = models.DateTimeField(blank=True, null=True)
    
    #dispatcher = models.ForeignKey(Dispatcher)
    
    class Meta:
        ordering = ('message_time',)
        
    def __unicode__(self):
        if self.message_type == self.MESSAGE_TYPE_OFFICE:
            return u"{} - Come to the Office".format(self.race_entry.racer)
        if self.message_type == self.MESSAGE_TYPE_DISPATCH:
            job_string = ""
            for job in self.jobs.all():
                job_string = "{} | {}".format(job_string, job)
            return u"{} - {}".format(self.race_entry.racer, job_string)    
            
    @property
    def message_type_as_string(self):
        return self.MESSAGE_TYPE_CHOICES[self.message_type][1]
    
    def message_body(self):
        pass
        return
    
    def confirm(self):
        pass
    
    def snooze(self):
        pass