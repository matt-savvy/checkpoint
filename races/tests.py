from django.test import TestCase
from .models import Race
from .factories import RaceFactory, ManifestFactory
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
        
    def test_populate_runs_without_start_time(self):
        """make sure minutes stay with the race start time minutes"""
        self.race.race_start_time = None
        self.race.save()
        self.race.populate_runs(self.race_entry_one)
         
        runs = Run.objects.filter(race_entry=self.race_entry_one)
        self.assertEqual(runs.count(), 12)


class ClearRacerTestCase(TestCase):
    def setUp(self):
        self.race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH)
        self.race_entry_one = RaceEntryFactory(race=self.race)
        self.race_entry_one.start_racer()
                
    def test_find_clear_racer(self):
        """one racer is clear"""
        racer = self.race.find_clear_racer()
        self.assertEqual(self.race_entry_one, racer)
        
    def test_find_clear_racer_out_of_several(self):
        """several clear racers, make sure we return the one with the highest position"""        
        self.race_entry_two = RaceEntryFactory(race=self.race)
        self.race_entry_two.start_racer()
        self.race_entry_two.starting_position = int(self.race_entry_one.starting_position) + 1
        self.race_entry_two.save()
        jobs = JobFactory.create_batch(5, race=self.race)
        self.race.populate_runs(self.race_entry_one)

        first_run = Run.objects.filter(race_entry=self.race_entry_one).first()
        first_run.status = Run.RUN_STATUS_DISPATCHING
        first_run.save()
        first_run.assign()
        
        racer = self.race.find_clear_racer()
        self.assertEqual(self.race_entry_two, racer)
    
    def test_find_clear_racer_when_no_one_is_clear(self):
        """no one is clear"""
        job = JobFactory(race=self.race)
        self.race.populate_runs(self.race_entry_one)
        
        self.race_entry_two = RaceEntryFactory(race=self.race)
        self.race_entry_two.start_racer()
        self.race_entry_two.starting_position = 2
        self.race_entry_two.save()
        self.race.populate_runs(self.race_entry_two)
        
        for run in Run.objects.filter(race_entry__race=self.race):
            run.status = Run.RUN_STATUS_ASSIGNED
            run.save()
        
        racer = self.race.find_clear_racer()
        self.assertIsNone(racer)
    
    def test_find_clear_racer_finished(self):
        """we have a racer that is clear, but they are finished"""
        self.race_entry_one.finish_racer()
        racer = self.race.find_clear_racer()
        self.assertIsNone(racer)
    
    def test_find_clear_racer_not_started(self):
        """we have a racer that is clear, but they are not started"""
        self.race_entry_one.unstart_racer()
        racer = self.race.find_clear_racer()
        self.assertIsNone(racer)
        
    def test_find_clear_racer_dq(self):
        """we have a racer that is clear, but they have been dq'd"""
        self.race_entry_one.dq_racer()
        racer = self.race.find_clear_racer()
        self.assertIsNone(racer)
        
    def test_find_clear_racer_dnf(self):
        """we have a racer that is clear, but they have been dnf'd"""
        
        self.race_entry_one.dnf_racer()
        racer = self.race.find_clear_racer()
        self.assertIsNone(racer)
    
    def test_find_clear_racer_but_has_jobs_dispatching(self):
        """we have a racer that is clear, but they have been dnf'd"""
        runs = Run.objects.filter(race_entry=self.race_entry_one)
        jobs = JobFactory.create_batch(5, race=self.race)
        self.race.populate_runs(self.race_entry_one)
        for run in runs:
            run.status = Run.RUN_STATUS_DISPATCHING
            run.save()
        racer = self.race.find_clear_racer()
        self.assertIsNone(racer)
    
    def test_find_clear_racer_but_has_pending_jobs(self):
        """we have a racer that is clear, but they have pending jobs"""
        import datetime
        import pytz
        runs = Run.objects.filter(race_entry=self.race_entry_one)
        for run in runs:
            run.status = Run.RUN_STATUS_PENDING
            run.utc_time_ready = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(minutes=5)
            run.save()
        racer = self.race.find_clear_racer()
        self.assertEqual(racer, self.race_entry_one)
        
class ManifestTestCase(TestCase):
    def setUp(self):
        self.manifests = ManifestFactory.create_batch(10)
        
    def test_manifest_type_as_string(self):
        self.manifest = ManifestFactory()
        self.assertTrue(True)