from django.test import TestCase
from raceentries.models import RaceEntry
from decimal import *
from django.test import TestCase
from dispatch.models import Message
from runs.models import Run
from races.models import Race, Manifest
from raceentries.models import RaceEntry
from dispatch.util import get_next_message
from jobs.factories import JobFactory
from races.factories import RaceFactory, ManifestFactory
from dispatch.factories import MessageFactory
from raceentries.factories import RaceEntryFactory
from runs.factories import RunFactory
import datetime
import pytz
import pdb
import decimal
from freezegun import freeze_time

class RaceEntryTestCase(TestCase):
        def setUp(self):
            self.right_now = datetime.datetime.now(tz=pytz.utc)
            self.race_one = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH_PRELIMS)
 
            self.manifest_one = ManifestFactory()
            self.manifest_two = ManifestFactory()
            
            self.race_entry_one = RaceEntryFactory(race=self.race_one, manifest=self.manifest_one, entry_status=RaceEntry.ENTRY_STATUS_ENTERED)
            self.race_entry_two = RaceEntryFactory(race=self.race_one)
            
            self.jobs_one = JobFactory.create_batch(10, race=self.race_one, manifest=self.manifest_one)
            self.jobs_one_start = JobFactory.create_batch(3, race=self.race_one, minutes_ready_after_start=0, manifest=self.manifest_one)
            self.jobs_two = JobFactory.create_batch(10, race=self.race_one, manifest=self.manifest_two)

        def test_start_racer_populates_jobs(self):
            "making sure that starting the racer populates jobs for dispatch prelimns"
            self.jobs_one = JobFactory.create_batch(13, race=self.race_one)
            self.race_entry_one.manifest = None
            self.race_entry_one.save()
            
            self.race_entry_one.start_racer()
            
            runs = Run.objects.filter(race_entry=self.race_entry_one)
            self.assertEqual(runs.count(), 13)
            
        def test_start_racer_populates_jobs_only_for_that_manifest(self):
            "making sure jobs for that manifest but only that manifest get populated"
            self.race_entry_one.entry_status = RaceEntry.ENTRY_STATUS_ENTERED
            self.race_entry_one.save()
            
            self.race_entry_one.start_racer()
            
            runs = Run.objects.filter(race_entry=self.race_entry_one)
            self.assertEqual(runs.count(), 13)
            
            for run in runs:
                self.assertEqual(run.job.manifest, self.manifest_one)
                self.assertNotEqual(run.job.manifest, self.manifest_two)
        
        def test_five_min_warning_false_with_no_limit(self):
            self.race_one.time_limit = 0
            self.race_one.race_start_time = self.right_now - datetime.timedelta(minutes=95)
            self.race_one.save()
            
            self.assertFalse(self.race_entry_one.five_minute_warning)
            
        def test_five_min_warning(self):
            self.race_one.time_limit = 100
            self.race_one.race_start_time = self.right_now - datetime.timedelta(minutes=95)
            self.race_one.save()
            
            self.assertTrue(self.race_entry_one.five_minute_warning)
            
        def test_five_min_warning_early(self):
            self.race_one.time_limit = 100
            self.race_one.race_start_time = self.right_now - datetime.timedelta(minutes=30)
            self.race_one.save()
            
            self.assertFalse(self.race_entry_one.five_minute_warning)
        
        def test_five_min_warning_prelim(self):
            self.race_one.time_limit = 100
            self.race_one.race_start_time = None
            self.race_entry_one.start_time = self.right_now - datetime.timedelta(minutes=95)
            self.race_one.save()
            self.race_entry_one.save()
            
            self.assertTrue(self.race_entry_one.five_minute_warning)
        
        def test_five_min_warning_early_prelim(self):
            self.race_one.time_limit = 100
            self.race_one.race_start_time = None
            self.race_entry_one.start_time = self.right_now - datetime.timedelta(minutes=30)
            self.race_one.save()
            self.race_entry_one.save()
            
            self.assertFalse(self.race_entry_one.five_minute_warning)
        
        @freeze_time("2018-9-27 10:30:00")
        def test_race_end_time_with_race_start_time(self):
            right_now = datetime.datetime.now(tz=pytz.utc)
            self.race_entry_one.start_racer()
            self.race_one.time_limit = 100
            self.race_one.race_start_time = right_now - datetime.timedelta(minutes=200)
            self.race_one.save()
            
            self.assertEqual(self.race_one.race_end_time, self.race_entry_one.race_end_time)
            
        @freeze_time("2018-9-27 10:30:00")
        def test_race_end_time_race_start_time_but_no_time_limit(self):
            right_now = datetime.datetime.now(tz=pytz.utc)
            self.race_entry_one.start_racer()
            self.race_one.race_start_time = right_now - datetime.timedelta(minutes=200)
            self.race_one.time_limit = 0
            self.race_one.save()
            self.race_entry_one.finish_racer()
            
            self.assertEqual(self.race_entry_one.race_end_time, datetime.datetime.now(tz=pytz.utc))
            
        @freeze_time("2018-9-27 10:30:00")
        def test_race_end_time_without_race_start_time(self):
            right_now = datetime.datetime.now(tz=pytz.utc)
            self.race_entry_one.start_racer()
            self.race_one.time_limit = 100
            self.race_one.race_start_time = None
            self.race_entry_one.finish_racer()
            one_hundred = self.race_entry_one.start_time + datetime.timedelta(minutes=100)
            
            self.assertEqual(self.race_entry_one.race_end_time, one_hundred)
        
        def test_finish_racer_deducts_late_jobs(self):
            """any jobs that are late when the race ends will get docked from your pay"""
            self.race_one.race_start_time = self.right_now - datetime.timedelta(minutes=60)
            self.race_one.time_limit = 60
            self.race_one.save()
            
            self.race_entry_one.start_racer()
            runs = Run.objects.filter(race_entry=self.race_entry_one)
            run = runs.first()
            run.assign(force=True)
            run.utc_time_due = self.right_now - datetime.timedelta(minutes=40)
            run.job.points = '5.00'
            run.job.save()
            run.save()
            
            self.race_entry_one.finish_racer()
            
            self.assertEqual(runs[0].points_awarded, decimal.Decimal('-5.00'))
            
class ScoreTestCase(TestCase):
    def setUp(self):
        self.race_one = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH_PRELIMS)
        self.race_entry_one = RaceEntryFactory(race=self.race_one, manifest=self.manifest_one, entry_status=RaceEntry.ENTRY_STATUS_ENTERED)
        self.jobs = JobFactory.create_batch(10, minutes_due_after_start=45, points="3.00", race=self.race_one, manifest=self.manifest_one)
        self.race_entry_one.start_racer()
