from django.db import models
from races.models import Race
from raceentries.models import RaceEntry
from jobs.models import Job
from runs.models import Run
import datetime
import pytz

class Message(models.Model):
    MESSAGE_TYPE_DISPATCH = 0
    MESSAGE_TYPE_OFFICE   = 1
    MESSAGE_TYPE_NOTHING  = 2
    MESSAGE_TYPE_ERROR    = 3
    
    MESSAGE_TYPE_CHOICES = (
        (MESSAGE_TYPE_DISPATCH, 'Dispatching Jobs'),
        (MESSAGE_TYPE_OFFICE, 'Come to the Office'),
        (MESSAGE_TYPE_NOTHING, "Nothing to dispatch."),
        (MESSAGE_TYPE_ERROR, "Some kind of error.")
    )
    
    MESSAGE_STATUS_NONE          = 0
    MESSAGE_STATUS_DISPATCHING   = 1
    MESSAGE_STATUS_SNOOZED       = 2
    MESSAGE_STATUS_CONFIRMED     = 3
    
    MESSAGE_STATUS_CHOICES = (
        (MESSAGE_STATUS_NONE, 'N/A'),
        (MESSAGE_STATUS_DISPATCHING, 'Dispatching / On screen'),
        (MESSAGE_STATUS_SNOOZED, "Dispatcher snoozed."),
        (MESSAGE_STATUS_CONFIRMED, "Rider Confirmed.")
    )
    
    race = models.ForeignKey(Race)
    race_entry = models.ForeignKey(RaceEntry, null=True)
    runs = models.ManyToManyField(Run)
    message_time = models.DateTimeField(blank=True, null=True)
    message_type = models.IntegerField(choices=MESSAGE_TYPE_CHOICES, default=MESSAGE_TYPE_DISPATCH)
    status = models.IntegerField(choices=MESSAGE_STATUS_CHOICES, default=MESSAGE_STATUS_NONE)
    confirmed_time = models.DateTimeField(blank=True, null=True)
    #dispatcher = models.ForeignKey(Dispatcher)
    
    class Meta:
        ordering = ('message_time',)
        
    def __unicode__(self):
        if self.message_type == self.MESSAGE_TYPE_OFFICE:
            return u"{} - Come to the Office".format(self.race_entry.racer)
        if self.message_type == self.MESSAGE_TYPE_DISPATCH:
            dispatch_string = "assign runs"
            return u"{} - {}".format(self.race_entry.racer, dispatch_string)  
        if self.message_type == self.MESSAGE_TYPE_ERROR:
            return u"ERROR"
        if self.message_type == self.MESSAGE_TYPE_NOTHING:
            return u"Blank Message"  
            
    @property
    def message_type_as_string(self):
        return self.MESSAGE_TYPE_CHOICES[self.message_type][1]
        
    @property
    def message_status_as_string(self):
        return self.MESSAGE_STATUS_CHOICES[self.status][1]
    
    def confirm(self):
        self.status = self.MESSAGE_STATUS_CONFIRMED
        self.confirmed_time = datetime.datetime.now(tz=pytz.utc)
        self.save()
        
        if self.message_type == self.MESSAGE_TYPE_DISPATCH:
            for run in self.runs.all():
                run.assign()
                
        elif self.message_type == self.MESSAGE_TYPE_OFFICE:
            self.race_entry.entry_status = RaceEntry.ENTRY_STATUS_CUT
            self.race_entry.save()
        
        #TODO add logging
        return self
    
    def snooze(self):
        self.message_time = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(seconds=60)
        self.status = self.MESSAGE_STATUS_SNOOZED
        self.save()
        for run in self.runs.all():
            run.status = Run.RUN_STATUS_DISPATCHING
            run.save()
        #TODO add logging
        return self
    