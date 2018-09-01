from django.test import TestCase
from checkpoints.models import Checkpoint
from racers.models import Racer
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

class MobileCheckpointTestCase(TestCase):
    def setUp(self):
        self.race = RaceFactory()
        self.racer_one = RacerFactory()
        self.racer_two = RacerFactory()
        self.checkpoint_one = CheckpointFactory()
        self.checkpoint_two = CheckpointFactory()
        self.job = JobFactory(race=self.race, pick_checkpoint=self.checkpoint_one, drop_checkpoint=self.checkpoint_two)
        self.job_two = JobFactory(race=self.race, pick_checkpoint=self.checkpoint_two, drop_checkpoint=self.checkpoint_one)
        self.race_entry_one = RaceEntryFactory(racer=self.racer_one, race=self.race)
        self.race_entry_two = RaceEntryFactory(racer=self.racer_two, race=self.race)
        self.run_one = RunFactory(job=self.job, race_entry=self.race_entry_one)
        self.run_two = RunFactory(job=self.job, race_entry=self.race_entry_two)
        
    def test_get_available_runs(self):
        """check to make sure that a run that should be IS available """
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertTrue(self.run_one in runs)
    
    def test_get_available_runs_only_correct_runs(self):
        """check to make sure it doesn't return a run that SHOULD NOT be available"""
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_two in runs)
        
    def test_get_available_runs_only_returns_assigned(self):
        """check to make sure that it only returns runs that are ASSIGNED so people aren't picking complete or already picked jobs"""
        run_three = RunFactory(job=self.job, race_entry=self.race_entry_one)
        self.run_one.pick()
        runs = get_available_runs(race_entry=self.race_entry_one, checkpoint=self.checkpoint_one)
        self.assertFalse(self.run_one in runs)
        self.assertTrue(run_three in runs)
        
        
        