from django.db import models
from jobs.models import Job
import datetime
import pytz
import decimal

class Run(models.Model):

    RUN_STATUS_PICKED               = 0
    RUN_STATUS_COMPLETED            = 1
    RUN_STATUS_ASSIGNED             = 2
    RUN_STATUS_PENDING              = 3
    
    RUN_STATUS_CHOICES = (
        (RUN_STATUS_PENDING, 'Pending'), ## job exists in the future for the rider but is not available yet
        (RUN_STATUS_ASSIGNED, 'Assigned'), ## job is assigned and active
        (RUN_STATUS_PICKED, 'Picked'), ## job is picked up
        (RUN_STATUS_COMPLETED, 'Completed') ##job is dropped
    )
    
    DETERMINATION_OK                = 1
    DETERMINATION_LATE              = 2
    DETERMINATION_NOT_DROPPED       = 3
    DETERMINATION_NOT_DETERMINED    = 4
    DETERMINATION_ERROR             = 9
    
    DETERMINATION_CHOICES = (
        (DETERMINATION_OK, 'OK'),
        (DETERMINATION_LATE, 'Late'),
        (DETERMINATION_NOT_DROPPED, 'Not Dropped'),
        (DETERMINATION_NOT_DETERMINED, 'Not Determined'),
        (DETERMINATION_ERROR, 'Error!')
    )
    
    
    job = models.ForeignKey(Job)
    race_entry = models.ForeignKey('raceentries.RaceEntry')
    status = models.IntegerField(choices=RUN_STATUS_CHOICES, default=RUN_STATUS_COMPLETED)
    determination = models.IntegerField(choices=DETERMINATION_CHOICES, default=DETERMINATION_OK)
    notes = models.TextField(blank=True)
    time_entered = models.DateTimeField(auto_now_add=True)
    points_awarded = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    utc_time_picked = models.DateTimeField(blank=True, null=True)
    utc_time_dropped = models.DateTimeField(blank=True, null=True)
    completion_seconds = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['job__minutes_ready_after_start']
    
    def __unicode__(self):
        return u"({}){}:{}".format(self.RUN_STATUS_CHOICES[self.status][1], self.race_entry.racer, self.job)
    
    def status_as_string(self):
        return self.RUN_STATUS_CHOICES[self.status][1]
    
    def determination_as_string(self):
        index = [i for i, v in enumerate(self.DETERMINATION_CHOICES) if v[0] == self.determination]
        return self.DETERMINATION_CHOICES[index[0]][1]
    
    #def pick(self, job, race_entry):
    #    self.job = job
    #    self.race_entry = race_entry
    #    self.status = self.RUN_STATUS_PICKED
    #    self.determination = self.DETERMINATION_NOT_DROPPED
    #    self.utc_time_picked = datetime.datetime.now(tz=pytz.utc)
    #    self.save()
    
    def pick(self):
        self.status = self.RUN_STATUS_PICKED
        self.determination = self.DETERMINATION_NOT_DROPPED
        self.utc_time_picked = datetime.datetime.now(tz=pytz.utc)
        self.save()
    
    def drop(self):
        self.utc_time_dropped = datetime.datetime.now(tz=pytz.utc)
        self.completion_seconds = (self.utc_time_dropped - self.utc_time_picked).seconds
        self.status = self.RUN_STATUS_COMPLETED
        
        if not self.race_entry.race.race_start_time:
            self.determination = self.DETERMINATION_ERROR
            self.save()
            return
        
        race = self.race_entry.race
        job_due_time = race.race_start_time.astimezone(pytz.utc) + datetime.timedelta(minutes=self.job.minutes_due_after_start)
        if self.utc_time_dropped <= job_due_time:
            self.determination = self.DETERMINATION_OK
            self.points_awarded = self.job.points
        else:
            self.determination = self.DETERMINATION_LATE
            self.points_awarded = decimal.Decimal('0.00')
        
        self.save()
        
            
    