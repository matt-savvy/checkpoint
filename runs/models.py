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
    RUN_STATUS_DISPATCHING          = 4
    
    RUN_STATUS_CHOICES = (
        (RUN_STATUS_PICKED, 'Picked'), ## job is picked up
        (RUN_STATUS_COMPLETED, 'Completed'), ##job is dropped
        (RUN_STATUS_ASSIGNED, 'Assigned'), ## job is assigned and active
        (RUN_STATUS_PENDING, 'Pending'), ## job exists in the future for the rider but is not available yet
        (RUN_STATUS_DISPATCHING, 'Dispatching') ## job is available and is in a message. so we don't double dispatch the same work.
    )
    
    DETERMINATION_OK                = 1
    DETERMINATION_LATE              = 2
    DETERMINATION_NOT_DROPPED       = 3
    DETERMINATION_NOT_DETERMINED    = 4
    DETERMINATION_NOT_PICKED        = 5
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
    status = models.IntegerField(choices=RUN_STATUS_CHOICES, default=RUN_STATUS_PENDING)
    determination = models.IntegerField(choices=DETERMINATION_CHOICES, default=DETERMINATION_NOT_DETERMINED)
    notes = models.TextField(blank=True)
    time_entered = models.DateTimeField(auto_now_add=True)
    points_awarded = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    utc_time_ready = models.DateTimeField(blank=True, null=True)
    utc_time_assigned = models.DateTimeField(blank=True, null=True)
    utc_time_due = models.DateTimeField(blank=True, null=True)
    utc_time_picked = models.DateTimeField(blank=True, null=True)
    utc_time_dropped = models.DateTimeField(blank=True, null=True)
    completion_seconds = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['utc_time_ready', 'race_entry__starting_position']
        
    def __unicode__(self):
        return u"({}){}:{}".format(self.RUN_STATUS_CHOICES[self.status][1], self.race_entry.racer, self.job)
    
    def status_as_string(self):
        return self.RUN_STATUS_CHOICES[self.status][1]
    
    def determination_as_string(self):
        index = [i for i, v in enumerate(self.DETERMINATION_CHOICES) if v[0] == self.determination]
        return self.DETERMINATION_CHOICES[index[0]][1]
    
    @property
    def localized_due_time(self):
        eastern = pytz.timezone('US/Eastern')
        if self.utc_time_due:
            return self.utc_time_due.astimezone(eastern).strftime('%I:%M %p')
        else:
            return "N/A"
            
    @property
    def localized_ready_time(self):
        eastern = pytz.timezone('US/Eastern')
        if self.utc_time_ready:
            return self.utc_time_ready.astimezone(eastern).strftime('%I:%M %p')
        else:
            return "N/A"
    
    def assign(self, force=False):
        time_now = datetime.datetime.now(tz=pytz.utc)
        if self.utc_time_ready:
            if time_now <= self.utc_time_ready and not force:
                return
        if self.status == self.RUN_STATUS_DISPATCHING or force:
            self.status = self.RUN_STATUS_ASSIGNED
            self.determination = self.DETERMINATION_NOT_PICKED
            self.utc_time_assigned = time_now
            self.utc_time_due = time_now + datetime.timedelta(minutes=self.job.minutes_due_after_start)
            self.save()
    
    def pick(self):
        if self.status == self.RUN_STATUS_ASSIGNED:
            self.status = self.RUN_STATUS_PICKED
            self.determination = self.DETERMINATION_NOT_DROPPED
            self.utc_time_picked = datetime.datetime.now(tz=pytz.utc)
            self.save()
            self.race_entry.last_action = self.utc_time_picked
            self.race_entry.save()
            print "{} picked up {}".format(self.race_entry.racer, self.job)
            
    def drop(self):
        if self.status == self.RUN_STATUS_PICKED:
            self.utc_time_dropped = datetime.datetime.now(tz=pytz.utc)
            self.race_entry.last_action = self.utc_time_dropped
            self.race_entry.save()
            try:
                self.completion_seconds = (self.utc_time_dropped - self.utc_time_picked).seconds
            except:
                pass
            self.status = self.RUN_STATUS_COMPLETED
        
            if not self.race_entry.race.race_start_time:
                self.determination = self.DETERMINATION_ERROR
                self.save()
                return
        
            race = self.race_entry.race
            if not self.utc_time_due:
                job_due_time = race.race_start_time.astimezone(pytz.utc) + datetime.timedelta(minutes=self.job.minutes_due_after_start)
            else:
                job_due_time = self.utc_time_due
            if self.utc_time_dropped <= job_due_time:
                self.determination = self.DETERMINATION_OK
                self.points_awarded = self.job.points
            else:
                self.determination = self.DETERMINATION_LATE
                self.points_awarded = decimal.Decimal('0.00')
            
            print "{} dropped off {}".format(self.race_entry.racer, self.job)
            self.save()
            
    @property       
    def late(self):
        if not self.utc_time_due:
            return False
            
        if self.status == self.RUN_STATUS_ASSIGNED or self.status == self.RUN_STATUS_PICKED:
            right_now = datetime.datetime.now(tz=pytz.utc)
            if right_now > self.utc_time_due:
                return True
        elif self.status == self.RUN_STATUS_COMPLETED:
            if not self.utc_time_dropped <= self.utc_time_due:
                return True
        return False
    