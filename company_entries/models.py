from django.db import models
from companies.models import Company
from races.models import Race
import datetime
import pytz
from django.utils.timezone import utc

class CompanyEntry(models.Model):
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
        (ENTRY_STATUS_PROCESSING, 'Company has finished the race and is waiting to finish'),
    )

    company = models.ForeignKey(Company)
    race = models.ForeignKey(Race)
    entry_date = models.DateTimeField(auto_now_add=True)
    entry_status = models.IntegerField(choices=ENTRY_STATUS_CHOICES, default=ENTRY_STATUS_ENTERED)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    final_time = models.IntegerField(default=0)

    dq_time = models.DateTimeField(blank=True, null=True)
    dq_reason = models.CharField(blank=True, max_length=255)

    scratch_pad = models.TextField(blank=True)

    class Meta:
        unique_together = (("company", "race"))

    def __unicode__(self):
        return u'{} in {}'.format(self.company.name, self.race)

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

    def get_race_entries(self):
        from raceentries.models import RaceEntry
        return RaceEntry.objects.filter(race=self.race).filter(racer__company=self.company)

    #METHODS!!
    #points_earned = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    #supplementary_points = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    #deductions = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    #grand_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    #number_of_runs_completed = models.IntegerField(default=0)

    def get_runs(self):
        from runs.models import Run
        return Run.objects.filter(company_entry=self)

    def populate_runs(self):
        runs = self.race.populate_runs(company_entry=self)

    def start_racers(self):
        entries = self.get_race_entries()
        for entry in entries:
            entry.start_racer()

        self.entry_status = self.ENTRY_STATUS_RACING
        self.start_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        self.populate_runs()

    def unstart_racers(self):
        from runs.models import Run

        entries = self.get_race_entries()
        for entry in entries:
            entry.unstart_racer()

        self.entry_status = self.ENTRY_STATUS_ENTERED
        self.start_time = None
        self.save()

        runs = Run.objects.filter(company_entry=self).delete()

    def finish_racers(self):
        entries = self.get_race_entries()
        for entry in entries:
            entry.finish_racer()

        self.entry_status = self.ENTRY_STATUS_FINISHED
        self.end_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
        ##score all jobs?
