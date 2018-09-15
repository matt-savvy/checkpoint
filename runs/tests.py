from django.test import TestCase
from .models import Run
from races.models import Race
from races.factories import RaceFactory
from jobs.factories import JobFactory
from raceentries.factories import RaceEntryFactory
import datetime
import pytz
        
class RunTestCase(TestCase):
    def setUp(self):
        self.right_now = datetime.datetime.now(tz=pytz.utc) 
        self.race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH, race_start_time=self.right_now)
        self.job = JobFactory(race=self.race, minutes_ready_after_start=0, minutes_due_after_start=20)
        self.race_entry_one = RaceEntryFactory(race=self.race)
        self.race_entry_two = RaceEntryFactory(race=self.race)
        self.race.populate_runs(self.race_entry_one)
        self.race.populate_runs(self.race_entry_two)
        self.runs = Run.objects.filter(race_entry=self.race_entry_one)
        for run in self.runs:
            run.status = Run.RUN_STATUS_DISPATCHING
        
    def test_assign(self):
        run = self.runs[0]
        run.assign()
        self.assertEqual(run.status, Run.RUN_STATUS_ASSIGNED)
        
    def test_assign_if_status_is_not_dispatching(self):
        run = self.runs[0]
        run.status = Run.RUN_STATUS_PENDING
        run.save()
        run.assign()
        self.assertEqual(run.status, Run.RUN_STATUS_PENDING)
    
    def test_assign_double_assign(self):
        run = self.runs[0]
        run.assign()
        run.assign()
        self.assertEqual(run.status, Run.RUN_STATUS_ASSIGNED)
        
    def test_assign_adds_due_time(self):
        run_obj = self.runs[0]
        run_obj.assign()
        twenty_mins_from_now = self.right_now + datetime.timedelta(minutes=20)
        self.assertIsNotNone(run_obj.utc_time_due)  
    
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