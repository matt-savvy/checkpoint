from django.db import models
import datetime

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
    race = models.ForeignKey(Race)
    manifest_name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)