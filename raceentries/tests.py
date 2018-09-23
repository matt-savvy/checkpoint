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


class RaceEntryTestCase(TestCase):
        def setUp(self):
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
                
class ScoreTestCase(TestCase):
    def setUp(self):
        self.race_one = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH_PRELIMS)
        self.race_entry_one = RaceEntryFactory(race=self.race_one, manifest=self.manifest_one, entry_status=RaceEntry.ENTRY_STATUS_ENTERED)
        self.jobs = JobFactory.create_batch(10, minutes_due_after_start=45, points="3.00", race=self.race_one, manifest=self.manifest_one)
        self.race_entry_one.start_racer()
