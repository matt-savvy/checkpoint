from django.test import TestCase
from .models import Race
from .factories import RaceFactory
from raceentries.factories import RaceEntryFactory
from jobs.factories import JobFactory
from runs.models import Run
from faker import Faker
import datetime
fake = Faker()


class RaceTestCase(TestCase):
    def setUp(self):
        self.race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH)
        self.race_entry_one = RaceEntryFactory()
        self.race_entry_two = RaceEntryFactory()
        self.jobs_first = JobFactory.create_batch(4, race=self.race, minutes_ready_after_start=0)
        self.jobs_second = JobFactory.create_batch(4, race=self.race, minutes_ready_after_start=5)
        self.jobs_third = JobFactory.create_batch(4, race=self.race, minutes_ready_after_start=10)
        
    def test_populate_runs_single_racer(self):
        """testing populating the runs for a single racer getting entered"""
        self.race.populate_runs(self.race_entry_one)
        runs = Run.objects.filter(race_entry=self.race_entry_one)
        self.assertEqual(runs.count(), 12)
        
    def test_populate_runs_only_correct_racer(self):
        """only runs for race_entry_one show up, not for race_entry_two"""
        self.race.populate_runs(self.race_entry_one)
        runs = Run.objects.filter(race_entry=self.race_entry_two)
        self.assertFalse(runs.exists())
    
    def test_populate_runs_with_start_time(self):
        """make sure minutes stay with the race start time minutes"""
        self.race.race_start_time = fake.future_datetime()
        time_plus_five = self.race.race_start_time + datetime.timedelta(minutes=5)
        self.race.save()
        self.race.populate_runs(self.race_entry_one)
         
        first_runs = Run.objects.filter(race_entry=self.race_entry_one).filter(utc_time_ready__lte=self.race.race_start_time)
        second_runs = Run.objects.filter(race_entry=self.race_entry_one).filter(utc_time_ready__lte=self.race.race_start_time + datetime.timedelta(minutes=5))
        third_runs = Run.objects.filter(race_entry=self.race_entry_one).filter(utc_time_ready__lte=self.race.race_start_time + datetime.timedelta(minutes=15))

        self.assertEqual(first_runs.count(), 4)
        self.assertEqual(second_runs.count(), 8)
        self.assertEqual(third_runs.count(), 12)
        
    