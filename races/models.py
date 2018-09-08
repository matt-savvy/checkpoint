from django.db import models
import datetime
from django.db.models import Q

class Race(models.Model):
    
    RACE_TYPE_PRELIMS = 0
    RACE_TYPE_FINALS = 1
    RACE_TYPE_DISPATCH = 2
    
    RACE_TYPE_CHOICES = (
        (RACE_TYPE_PRELIMS, 'Prelims'),
        (RACE_TYPE_FINALS, 'Finals'),
        (RACE_TYPE_DISPATCH, 'Dispatch')
    )
    
    """(Race description)"""
    race_name = models.CharField(max_length=100)
    race_type = models.IntegerField(choices=RACE_TYPE_CHOICES, default=RACE_TYPE_PRELIMS)
    time_limit = models.IntegerField(default=0)
    race_start_time = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.race_name
    
    def get_absolute_url(self):
        return "/races/details/" + str(self.id) + "/"
    
    def find_clear_racer(self):
        from raceentries.models import RaceEntry
        from runs.models import Run
        from dispatch.models import Message

        race_entries = RaceEntry.objects.filter(race=self).filter(Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT))
        for race_entry in race_entries:
            run_count = Run.objects.filter(race_entry=race_entry).filter(Q(status=Run.RUN_STATUS_ASSIGNED) | Q(status=Run.RUN_STATUS_DISPATCHING)).count()
            
            #befre we do say they're clear, let's make sure a message for them isn't already on someone's screen
            current_message = Message.objects.filter(race=self).filter(race_entry=race_entry).filter(status=Message.MESSAGE_STATUS_DISPATCHING)
            if not current_message and run_count == 0:
                return race_entry
        return 
    
    def populate_runs(self, race_entry):
        from raceentries.models import RaceEntry
        from jobs.models import Job
        from runs.models import Run
        runs = []
        
        if self.race_type == self.RACE_TYPE_DISPATCH:
            jobs = Job.objects.filter(race=self)
            
            for job in jobs:
                run = Run(job=job, race_entry=race_entry, status=Run.RUN_STATUS_PENDING)
                if self.race_start_time:
                    run.utc_time_ready = self.race_start_time + datetime.timedelta(minutes=job.minutes_ready_after_start)
                run.save()
                runs.append(run)
        return runs
    
    @property
    def race_type_string(self):
        return self.RACE_TYPE_CHOICES[self.race_type][1]

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