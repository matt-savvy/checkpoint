from django.test import TestCase
from checkpoints.models import Checkpoint
from racers.models import Racer
from racers.factories import RacerFactory
from checkpoints.factories import CheckpointFactory
from races.factories import RaceFactory
from raceentries.models import RaceEntry
from jobs.factories import JobFactory
from jobs.models import Job
from runs.models import Run
import pdb

class MobileCheckpointTestCase(TestCase):
    def setUp(self):
        race = RaceFactory()
        racer_one = RacerFactory()
        racer_two = RacerFactory()
        checkpoint_one = CheckpointFactory()
        checkpoint_two = CheckpointFactory()
        
        pdb.set_trace()
        
    def test_get_available_jobs(self):
        pass