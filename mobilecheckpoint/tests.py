from django.test import TestCase
from checkpoints.models import Checkpoint
from racers.models import Racer
from races.models import Race
from racers.factories import RacerFactory
from checkpoints.factories import CheckpointFactory
from races.factories import RaceFactory
from raceentries.models import RaceEntry
from runs.factories import RunFactory
from raceentries.factories import RaceEntryFactory
from jobs.factories import JobFactory
from jobs.models import Job
from runs.models import Run
from mobilecheckpoint.util import get_available_runs
import pdb
import datetime
import pytz

class MobileCheckpointTestCase(TestCase):
    def setUp(self):
        right_now = datetime.datetime.now(tz=pytz.utc)
        self.race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH_FINALS, race_start_time=right_now)
        self.racer_one = RacerFactory()
        self.racer_two = RacerFactory()
        self.checkpoint_one = CheckpointFactory()
        self.checkpoint_two = CheckpointFactory()
        self.checkpoint_three = CheckpointFactory()
        self.job = JobFactory(race=self.race, pick_checkpoint=self.checkpoint_one, drop_checkpoint=self.checkpoint_two, minutes_ready_after_start=0)
        self.job_two = JobFactory(race=self.race, pick_checkpoint=self.checkpoint_two, drop_checkpoint=self.checkpoint_one, minutes_ready_after_start=0)
        self.job_three = JobFactory(race=self.race, pick_checkpoint=self.checkpoint_two, drop_checkpoint=self.checkpoint_three, minutes_ready_after_start=0)
        
        self.race_entry_one = RaceEntryFactory(racer=self.racer_one, race=self.race, entry_status=RaceEntry.ENTRY_STATUS_RACING)
        self.race_entry_two = RaceEntryFactory(racer=self.racer_two, race=self.race, entry_status=RaceEntry.ENTRY_STATUS_RACING)
        self.run_one = RunFactory(job=self.job, race_entry=self.race_entry_one)
        
        self.run_two_one = RunFactory(job=self.job, race_entry=self.race_entry_two)
        self.run_two_two = RunFactory(job=self.job_two, race_entry=self.race_entry_two)
        self.run_two_three = RunFactory(job=self.job_three, race_entry=self.race_entry_two)
        
        self.run_one.status = Run.RUN_STATUS_DISPATCHING
        self.run_one.assign()
        
    def test_get_available_runs(self):
        """check to make sure that a run that should be IS available """
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertTrue(self.run_one in runs)
    
    def test_run_pending(self):
        self.run_one.status = Run.RUN_STATUS_PENDING
        self.run_one.save()
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_one in runs)
        
    def test_run_already_picked(self):
        self.run_one.status = Run.RUN_STATUS_PICKED
        self.run_one.save()
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_one in runs)
        
    def test_run_already_complete(self):
        self.run_one.status = Run.RUN_STATUS_COMPLETED
        self.run_one.save()
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_one in runs)
    
    def test_run_dispatching(self):
        self.run_one.status = Run.RUN_STATUS_DISPATCHING
        self.run_one.save()
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_one in runs)
        
    def test_racer_dq(self):
        self.race_entry_one.dq_racer()
        
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_one in runs)
        
    def test_racer_dnf(self):
        self.race_entry_one.dnf_racer()
        
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_one in runs)
    
    def test_wrong_racer(self):
        runs = get_available_runs(race_entry=self.race_entry_two, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_one in runs)
        
    def test_multiple_runs(self):
        self.run_two_one.status = Run.RUN_STATUS_ASSIGNED
        self.run_two_one.save()
        self.run_two_two.status = Run.RUN_STATUS_ASSIGNED
        self.run_two_two.save()
        self.run_two_three.status = Run.RUN_STATUS_ASSIGNED
        self.run_two_three.save()
        
        runs = get_available_runs(race_entry=self.race_entry_two, checkpoint=self.checkpoint_two)
        
        self.assertFalse(self.run_one in runs)
        self.assertFalse(self.run_two_one in runs)
        self.assertTrue(self.run_two_two in runs)
        self.assertTrue(self.run_two_three in runs)
    
    def test_diffent_checkpoint(self):
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_two)
        self.assertFalse(self.run_one in runs)