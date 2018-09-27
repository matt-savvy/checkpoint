from django.db import models
import datetime
import pytz
from django.db.models import Q

class Race(models.Model):
    
    RACE_TYPE_PRELIMS = 0
    RACE_TYPE_FINALS = 1
    RACE_TYPE_DISPATCH_PRELIMS = 2
    RACE_TYPE_DISPATCH_FINALS = 3
    
    RACE_TYPE_CHOICES = (
        (RACE_TYPE_PRELIMS, 'Prelims'),
        (RACE_TYPE_FINALS, 'Finals'),
        (RACE_TYPE_DISPATCH_PRELIMS, 'Dispatched Individual Heats'),
        (RACE_TYPE_DISPATCH_FINALS, 'Dispatched Group Finals')
    )
    
    OPEN_RUN_LIMIT = 13
    OVERTIME_RUN_LIMIT = 6 
    
    """(Race description)"""
    race_name = models.CharField(max_length=100)
    race_type = models.IntegerField(choices=RACE_TYPE_CHOICES, default=RACE_TYPE_PRELIMS)
    time_limit = models.IntegerField(default=0)
    race_start_time = models.DateTimeField(blank=True, null=True)
    overtime = models.BooleanField(default=False)

    def __unicode__(self):
        return self.race_name
    
    def get_absolute_url(self):
        return "/races/details/" + str(self.id) + "/"
    
    @property
    def dispatch_race(self):
        if self.race_type == self.RACE_TYPE_DISPATCH_PRELIMS or self.race_type == self.RACE_TYPE_DISPATCH_FINALS:
            return True
        return False
    
    def find_clear_racer(self):
        from raceentries.models import RaceEntry
        from runs.models import Run
        from dispatch.models import Message
        
        race_entries = RaceEntry.objects.filter(race=self).filter(Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT))
        for race_entry in race_entries:
            ##do they have any assigned jobs or jobs that are currently being dispatched?
            run_count = Run.objects.filter(race_entry=race_entry).filter(Q(status=Run.RUN_STATUS_ASSIGNED) | Q(status=Run.RUN_STATUS_PICKED) | Q(status=Run.RUN_STATUS_DISPATCHING)).count()
            
            if run_count == 0:
                #befre we do say they're clear, let's make sure a message for them isn't already on someone's screen
                current_message = Message.objects.filter(race_entry=race_entry).filter(status=Message.MESSAGE_STATUS_DISPATCHING).exists()
            
                #if they're clear AND cut, we see if they have already 10-4'd a request to come to the office
                already_confirmed_cut = Message.objects.filter(race_entry=race_entry).filter(message_type=Message.MESSAGE_TYPE_OFFICE).filter(Q(status=Message.MESSAGE_STATUS_CONFIRMED) | Q(status=Message.MESSAGE_STATUS_SNOOZED)).exists()
            
                if not current_message and not already_confirmed_cut:
                    return race_entry
            
        return
    
    def populate_runs(self, race_entry):
        from raceentries.models import RaceEntry
        from jobs.models import Job
        from runs.models import Run
        runs = []

        if self.dispatch_race:
            jobs = Job.objects.filter(race=self).filter(Q(manifest=race_entry.manifest) | Q(manifest=None))
            
            for job in jobs:
                run = Run(job=job, race_entry=race_entry, status=Run.RUN_STATUS_PENDING)
                if self.race_type == self.RACE_TYPE_DISPATCH_FINALS:
                    if self.race_start_time:
                        ready_time = self.race_start_time
                    else:
                        ready_time = datetime.datetime.now(tz=pytz.utc)
                elif self.race_type == self.RACE_TYPE_DISPATCH_PRELIMS:
                    ready_time = race_entry.start_time
                run.utc_time_ready = ready_time + datetime.timedelta(minutes=job.minutes_ready_after_start)
                run.save()
                runs.append(run)
                if self.race_type == self.RACE_TYPE_DISPATCH_FINALS:
                    if job.minutes_ready_after_start == 0:
                        run.assign(force=True)
        return runs
    
    def redo_run_math(self):
        from runs.models import Run
        if self.race_type == self.RACE_TYPE_DISPATCH_FINALS:
            runs = Run.objects.filter(race_entry__race=self)
            for run in runs:
                if self.race_start_time:
                    ready_time = self.race_start_time
                else:
                    ready_time = datetime.datetime.now(tz=pytz.utc)
                run.utc_time_ready = ready_time + datetime.timedelta(minutes=run.job.minutes_ready_after_start)
                run.save()
                
    @property
    def race_type_string(self):
        return self.RACE_TYPE_CHOICES[self.race_type][1]
        
    @property
    def run_limit(self):
        if self.overtime:
            return self.OVERTIME_RUN_LIMIT   
        return self.OPEN_RUN_LIMIT

class Manifest(models.Model):
    """jobs will belong to a manifest, so we can have different sets of jobs for the same race"""
    TYPE_CHOICE_STARTING = 0
    TYPE_CHOICE_MAIN     = 1
    TYPE_CHOICE_BONUS    = 2
    
    TYPE_CHOICES = (
        (TYPE_CHOICE_STARTING, 'Starting Manifest'),
        (TYPE_CHOICE_MAIN, 'Main Manifest'),
        (TYPE_CHOICE_BONUS, 'Overtime Manifest')
    )
    
    race = models.ForeignKey(Race)
    manifest_name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    manifest_type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_CHOICE_MAIN)
    cut_off_minutes_after_start = models.IntegerField(default=9999)
    
    class Meta:
        ordering = ['manifest_type', 'order']
    
    def __unicode__(self):
        return u"Manifest #{} for {} ({})".format(self.order, self.race, self.manifest_name)
        
    @property
    def manifest_type_as_string(self):
        return self.TYPE_CHOICES[self.manifest_type][1]
        
    def jobs(self):
        from jobs.models import Job
        return Job.objects.filter(race=race, manifest=self)