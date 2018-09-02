from django.test import TestCase
from .models import Run
from races.models import Race
from races.factories import RaceFactory
from jobs.factories import JobFactory
from raceentries.factories import RaceEntryFactory

class RunTestCase(TestCase):
    def setUp(self):
        self.race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH)
        self.job = JobFactory(race=self.race, minutes_ready_after_start=0)
        self.race_entry_one = RaceEntryFactory(race=self.race)
        self.race_entry_two = RaceEntryFactory(race=self.race)
        self.race.populate_runs(self.race_entry_one)
        import pdb
        #pdb.set_trace()
        self.race.populate_runs(self.race_entry_two)
        self.runs = Run.objects.filter(race_entry=self.race_entry_one)
        
    def test_assign(self):
        run = self.runs[0]
        run.assign()
        self.assertEqual(run.status, Run.RUN_STATUS_ASSIGNED)
    
    def test_assign_double_assign(self):
        run = self.runs[0]
        run.assign()
        run.assign()
        self.assertEqual(run.status, Run.RUN_STATUS_ASSIGNED)
        
    def test_pick_without_assign(self):
        run = self.runs[0]
        run.pick()
        self.assertNotEqual(run.status, Run.RUN_STATUS_PICKED)
        
    def test_drop_without_assign(self):
        run = self.runs[0]
        run.drop()
        self.assertNotEqual(run.status, Run.RUN_STATUS_COMPLETED)
        
    def test_drop_without_pick(self):
        run = self.runs[0]
        run.assign()
        run.drop()
        self.assertNotEqual(run.status, Run.RUN_STATUS_COMPLETED)
        self.assertEqual(run.status, Run.RUN_STATUS_ASSIGNED)
    
    def test_drop(self):
        run = self.runs[0]
        run.assign()
        run.pick()
        run.drop()
        self.assertEqual(run.status, Run.RUN_STATUS_COMPLETED)