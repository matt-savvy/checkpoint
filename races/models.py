from django.db import models
import datetime
import pytz
from django.db.models import Q
from companies.models import Company

class Race(models.Model):

    RACE_TYPE_PRELIMS = 0
    RACE_TYPE_FINALS = 1
    RACE_TYPE_DISPATCH_PRELIMS = 2
    RACE_TYPE_DISPATCH_FINALS = 3
    RACE_TYPE_COMPANY_RACE = 4


    RACE_TYPE_CHOICES = (
        (RACE_TYPE_PRELIMS, 'Prelims'),
        (RACE_TYPE_FINALS, 'Finals'),
        (RACE_TYPE_DISPATCH_PRELIMS, 'Dispatched Individual Heats'),
        (RACE_TYPE_DISPATCH_FINALS, 'Dispatched Group Finals'),
        (RACE_TYPE_COMPANY_RACE, 'Company Race'),
    )

    OPEN_RUN_LIMIT = 13
    OVERTIME_RUN_LIMIT = 6

    """(Race description)"""
    race_name = models.CharField(max_length=100)
    race_type = models.IntegerField(choices=RACE_TYPE_CHOICES, default=RACE_TYPE_COMPANY_RACE)
    time_limit = models.IntegerField(default=0)
    race_start_time = models.DateTimeField(blank=True, null=True)
    overtime = models.BooleanField(default=False)

    def __unicode__(self):
        return self.race_name

    def get_absolute_url(self):
        return "/races/details/" + str(self.id) + "/"

    def add_company(self, company):
        from company_entries.models import CompanyEntry
        from raceentries.models import RaceEntry
        company_entry = CompanyEntry(company=company, race=self)
        company_entry.save()

        racers = company.get_racers()

        for racer in racers:
            race_entry = RaceEntry(race=self, racer=racer)
            race_entry.save()
            print(race_entry)

        return company_entry

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

    def populate_runs(self, race_entry=None, company_entry=None):
        from raceentries.models import RaceEntry
        from jobs.models import Job
        from runs.models import Run
        print("populate runs")
        runs = []

        if not race_entry and not company_entry:
            return False

        if self.dispatch_race:

            overtime_manifest = Manifest.objects.filter(race=self).filter(manifest_type=Manifest.TYPE_CHOICE_BONUS).first()
            jobs = Job.objects.filter(race=self)

            if race_entry.manifest:
                jobs = jobs.filter(Q(manifest=race_entry.manifest) | Q(manifest=None))
            else:
                jobs = jobs.filter(manifest=None)

            if overtime_manifest:
                overtime_jobs = Job.objects.filter(race=self).filter(manifest=overtime_manifest)
                jobs = jobs | overtime_jobs

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
        else:
            jobs = Job.objects.filter(race=self)
            for job in jobs:
                run = Run(job=job, company_entry=company_entry, status=Run.RUN_STATUS_PENDING)

                if self.race_start_time:
                    ready_time = self.race_start_time
                else:
                    ready_time = datetime.datetime.now(tz=pytz.utc)

                run.utc_time_ready = ready_time + datetime.timedelta(minutes=job.minutes_ready_after_start)
                run.utc_time_due = run.utc_time_ready + datetime.timedelta(minutes=job.minutes_due_after_start)
                run.save()
                runs.append(run)

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

    @property
    def five_minute_warning(self):
        if self.time_limit == 0:
            return False

        if self.race_start_time:
            five_mins_from_finish = self.race_start_time + datetime.timedelta(minutes=self.time_limit - 5)
            right_now = datetime.datetime.now(tz=pytz.utc)
            if right_now >= five_mins_from_finish:
                return True

        return False

    @property
    def race_end_time(self):
        if self.race_start_time and self.time_limit != 0:
            end_time = self.race_start_time + datetime.timedelta(minutes=self.time_limit)
            return end_time

        return None



class Manifest(models.Model):
    """jobs will belong to a manifest, so we can have different sets of jobs for the same race"""
    TYPE_CHOICE_STARTING = 0
    TYPE_CHOICE_BONUS    = 1


    TYPE_CHOICES = (
        (TYPE_CHOICE_STARTING, 'Starting Manifest'),
        (TYPE_CHOICE_BONUS, 'Overtime Manifest')
    )

    race = models.ForeignKey(Race)
    manifest_name = models.CharField(max_length=100)
    manifest_type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_CHOICE_STARTING)


    class Meta:
        ordering = ['manifest_type']
        unique_together = ('manifest_name', 'race')

    def __unicode__(self):
        return u"{} Manifest - {} ({})".format(self.manifest_name, self.race, self.manifest_type_as_string)

    def get_absolute_url(self):
        return "/races/manifests/details/" + str(self.id) + "/"

    @property
    def manifest_type_as_string(self):
        return self.TYPE_CHOICES[self.manifest_type][1]

    def jobs(self):
        from jobs.models import Job
        return Job.objects.filter(race=self.race).filter(manifest=self).order_by('minutes_ready_after_start')
