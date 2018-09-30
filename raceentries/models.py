from django.db import models
from racers.models import Racer
from races.models import Race, Manifest
import datetime
from django.utils.timezone import utc
from racecontrol.models import RaceControl
from runs.models import Run
from django.db.models import Q, Sum
import decimal
import pytz

class RaceEntry(models.Model):
    ENTRY_STATUS_ENTERED    = 0
    ENTRY_STATUS_RACING     = 1
    ENTRY_STATUS_FINISHED   = 2
    ENTRY_STATUS_DQD        = 3
    ENTRY_STATUS_DNF        = 4
    ENTRY_STATUS_PROCESSING = 5
    ENTRY_STATUS_CUT        = 6
    
    ENTRY_STATUS_CHOICES = (
        (ENTRY_STATUS_ENTERED, 'Entered'),
        (ENTRY_STATUS_RACING, 'Racing'),
        (ENTRY_STATUS_FINISHED, 'Finished'),
        (ENTRY_STATUS_DQD, 'Disqualified'),
        (ENTRY_STATUS_DNF, 'Did not finish'),
        (ENTRY_STATUS_PROCESSING, 'Racer has finished the race and is waiting to finish'),
        (ENTRY_STATUS_CUT, 'Not finished yet but will be given no more jobs, only a "come to the office" message'),
    )
    
    """(RaceEntry description)"""
    racer = models.ForeignKey(Racer)
    #race = models.ForeignKey(Race, related_name="raceentry", default=RaceControl.shared_instance().current_race)
    race = models.ForeignKey(Race)
    entry_date = models.DateTimeField(auto_now_add=True)
    last_action = models.DateTimeField(blank=True, null=True)
    entry_status = models.IntegerField(choices=ENTRY_STATUS_CHOICES, default=ENTRY_STATUS_ENTERED)
    
    starting_position = models.IntegerField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    final_time = models.IntegerField(default=0)
    
    dq_time = models.DateTimeField(blank=True, null=True)
    dq_reason = models.CharField(blank=True, max_length=255)
    
    points_earned = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    supplementary_points = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    deductions = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    grand_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    number_of_runs_completed = models.IntegerField(default=0)
        
    scratch_pad = models.TextField(blank=True)
    manifest = models.ForeignKey(Manifest, blank=True, null=True)
    
    class Meta:
        unique_together = (("racer", "race"), ("race", "starting_position"))
        ordering = ['starting_position']

    def __unicode__(self):
        return u"{} in {}".format(self.racer, self.race)
    
    @property
    def entry_status_as_string(self):
        if self.entry_status == self.ENTRY_STATUS_ENTERED:
            return 'Not Raced'
        elif self.entry_status == self.ENTRY_STATUS_RACING:
            return 'Racing'
        elif self.entry_status == self.ENTRY_STATUS_FINISHED:
            return 'Finished'
        elif self.entry_status == self.ENTRY_STATUS_DQD:
            return 'Disqualified ({})'.format(self.dq_reason)
        elif self.entry_status == self.ENTRY_STATUS_DNF:
            return 'Did Not Finish'
        elif self.entry_status == self.ENTRY_STATUS_PROCESSING:
            return 'Processing'
        elif self.entry_status == self.ENTRY_STATUS_CUT:
            from dispatch.models import Message
            message = Message.objects.filter(race_entry=self).filter(message_type=Message.MESSAGE_TYPE_OFFICE).filter(status=Message.MESSAGE_STATUS_CONFIRMED)
            if message.exists():
                eastern = pytz.timezone('US/Eastern')
                return 'Cut, racer copied at {}'.format(message.first().confirmed_time.astimezone(eastern).strftime('%I:%M %p'))
            else:
                return 'Cut, racer not messaged yet.'                    
        return 'Did Not Finish'
    
    def start_racer(self):
        if self.entry_status == self.ENTRY_STATUS_ENTERED:
            self.entry_status = self.ENTRY_STATUS_RACING
            self.start_time = datetime.datetime.utcnow().replace(tzinfo=utc)
            self.points_earned = '0.00'
            self.deductions = '0.00'
            self.grand_total = '0.00'
            self.last_action = self.start_time
            self.save()
            if self.race.race_type == Race.RACE_TYPE_DISPATCH_PRELIMS:
                runs = self.race.populate_runs(self)
            return True
        return False
    
    def unstart_racer(self):
        if self.entry_status == self.ENTRY_STATUS_RACING:
            self.entry_status = self.ENTRY_STATUS_ENTERED
            self.start_time = None
            self.points_earned = '0.00'
            self.deductions = '0.00'
            self.grand_total = '0.00'
            self.last_action = self.start_time
            self.save()
            if self.race.race_type == Race.RACE_TYPE_DISPATCH_PRELIMS:
                Run.objects.filter(race_entry=self).delete()
            if self.race.dispatch_race:
                from dispatch.models import Message
                Message.objects.filter(race_entry=self).delete()   
            return True
        return False
    
    def cut_racer(self):
        if self.entry_status == self.ENTRY_STATUS_RACING:
            self.entry_status = self.ENTRY_STATUS_CUT
            self.save()
            return True
            #TODO log
        return False
    
    def finish_racer(self):
        from runs.models import Run
        if self.entry_status == self.ENTRY_STATUS_RACING or self.entry_status == self.ENTRY_STATUS_CUT:
            self.entry_status = self.ENTRY_STATUS_FINISHED
            self.end_time = datetime.datetime.utcnow().replace(tzinfo=utc)
            time_diff = self.end_time - self.start_time
            self.final_time = time_diff.seconds
            self.save()
            
            import pdb
            #pdb.set_trace()
            runs = Run.objects.filter(Q(status=Run.RUN_STATUS_ASSIGNED) | Q(status=Run.RUN_STATUS_PICKED)).filter(race_entry=self).filter(utc_time_due__lte=self.race_end_time)
            for run in runs:
                run.determination = Run.DETERMINATION_NOT_DROPPED
                run.points_awarded = decimal.Decimal(-run.job.points)
                run.save()
            
            return True
        elif self.entry_status == self.ENTRY_STATUS_PROCESSING:
            self.entry_status = self.ENTRY_STATUS_FINISHED
            self.save()
            return True
        return False
        
    def dq_racer(self):
        self.entry_status = self.ENTRY_STATUS_DQD
        self.dq_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        return True
    
    def un_dq_racer(self):
        self.dq_time = None
        self.dq_reason = ''
        if self.final_time > 0:
            self.entry_status = self.ENTRY_STATUS_FINISHED
        else:
            self.entry_status = self.ENTRY_STATUS_RACING
        self.save()
        return True
    
    def dnf_racer(self):
        self.entry_status = self.ENTRY_STATUS_DNF
        self.save()
        return True
    
    def un_dnf_racer(self):
        self.entry_status = self.ENTRY_STATUS_RACING
        self.save()
        return True
    
    def add_up_points(self):
        runs = Run.objects.filter(race_entry__racer=self.racer).filter(job__race=self.race)
        total = decimal.Decimal('0.00')
        for run in runs:
            total += run.points_awarded
        self.points_earned = total
        self.calculate_grand_total()
    
    def add_up_runs(self):
        self.number_of_runs_completed = Run.objects.filter(race_entry=self).filter(status=Run.RUN_STATUS_COMPLETED).count()
    
    def calculate_grand_total(self):
        self.grand_total = (decimal.Decimal(self.points_earned) + decimal.Decimal(self.supplementary_points)) - decimal.Decimal(self.deductions)
    
    def calculate_current_score(self):
        right_now = datetime.datetime.now(tz=pytz.utc)
        points_aggregate = Run.objects.filter(race_entry=self).filter(status=Run.RUN_STATUS_COMPLETED).aggregate(points=Sum('points_awarded'))
        points = points_aggregate['points']
        if not points:
            points = decimal.Decimal('0.00')
        credit_jobs = Run.objects.filter(race_entry=self).filter(status=Run.RUN_STATUS_PICKED).filter(utc_time_due__lt=right_now).aggregate(points=Sum('job__points'))
        penalty_jobs = Run.objects.filter(race_entry=self).filter(Q(status=Run.RUN_STATUS_PICKED) | Q(status=Run.RUN_STATUS_ASSIGNED)).filter(utc_time_due__lt=right_now).aggregate(points=Sum('job__points'))

        if penalty_jobs['points']:
            points -= penalty_jobs['points']
        if credit_jobs['points']:
            points += (decimal.Decimal('.40') * credit_jobs['points'])
        return round(points, 2)
    
    def time_due_back(self, tz):
        due_back = self.start_time + datetime.timedelta(seconds=self.race.time_limit * 60)
        return due_back.astimezone(tz)
    
    @property
    def current_elapsed_time(self):
        if self.entry_status == self.ENTRY_STATUS_RACING:
            time_passed = datetime.datetime.utcnow().replace(tzinfo=utc) - self.start_time
            m, s = divmod(time_passed.seconds, 60)
            h, m = divmod(m, 60)
            return "%02d:%02d:%02d" % (h, m, s)
        elif self.entry_status == self.ENTRY_STATUS_FINISHED:
            return self.final_time_formatted
        return None
    
    @property
    def final_time_formatted(self):
        m, s = divmod(self.final_time, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)
            
    @property
    def localized_start_time(self):
        eastern = pytz.timezone('US/Eastern')
        if self.start_time:
            return self.start_time.astimezone(eastern).strftime('%I:%M %p')
        else:
            return "N/A"
    
    @property
    def number_of_open_jobs(self):
        runs = Run.objects.filter(race_entry=self).filter(Q(status=Run.RUN_STATUS_ASSIGNED) | Q(status=Run.RUN_STATUS_DISPATCHING) | Q(status=Run.RUN_STATUS_PICKED)).count()
        return runs
    
    @property
    def five_minute_warning(self):
        """if there's less than five minutes left in the race"""
        right_now = datetime.datetime.now(tz=pytz.utc)
        if self.race.time_limit == 0:
            return False
            
        if self.race.race_start_time:
            five_mins_from_finish = self.race.race_start_time + datetime.timedelta(minutes=self.race.time_limit-5)
        else:
            five_mins_from_finish = self.start_time + datetime.timedelta(minutes=self.race.time_limit-5)
        if right_now >= five_mins_from_finish:
            return True
        
        return False
    
    @property
    def race_end_time(self):
        if self.race.race_end_time:
            return self.race.race_end_time
        
        elif self.race.time_limit != 0:
            if self.start_time:
                return self.start_time + datetime.timedelta(minutes=self.race.time_limit)
        return self.end_time