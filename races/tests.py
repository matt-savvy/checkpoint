from django.test import TestCase
from .models import Race
from .factories import RaceFactory, ManifestFactory
from raceentries.factories import RaceEntryFactory
from jobs.factories import JobFactory
from runs.models import Run
from faker import Faker
import datetime
import pytz
fake = Faker()

class RaceTestCase(TestCase):
    def setUp(self):
        self.race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH_FINALS)
        self.race_entry_one = RaceEntryFactory(race=self.race)
        self.race_entry_two = RaceEntryFactory(race=self.race)
        self.jobs_first = JobFactory.create_batch(4, race=self.race, minutes_ready_after_start=0)
        self.jobs_second = JobFactory.create_batch(4, race=self.race, minutes_ready_after_start=5)
        self.jobs_third = JobFactory.create_batch(4, race=self.race, minutes_ready_after_start=10)
        
    def test_populate_runs_single_racer(self):
        """testing populating the runs for a single racer getting entered"""
        self.race.race_type = Race.RACE_TYPE_DISPATCH_PRELIMS
        self.race.save()
        self.race_entry_one.start_racer()
        runs = Run.objects.filter(race_entry=self.race_entry_one)
        self.assertEqual(runs.count(), 12)
        
    def test_populate_runs_only_correct_racer(self):
        """only runs for race_entry_one show up, not for race_entry_two"""
        self.race.race_type = Race.RACE_TYPE_DISPATCH_PRELIMS
        self.race_entry_one.start_racer()
        runs = Run.objects.filter(race_entry=self.race_entry_two)
        self.assertFalse(runs.exists())
        self.assertTrue(Run.objects.filter(race_entry=self.race_entry_one).exists())
    
    def test_populate_runs_with_start_time(self):
        """make sure minutes stay with the race start time minutes"""
        self.race.race_start_time = fake.future_datetime().replace(tzinfo=pytz.utc)
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
        
    def test_populate_runs_assigns_initial_jobs(self):
        for job in self.jobs_first:
            job.minutes_ready_after_start = 0
            job.save()
            
        self.race.race_start_time = fake.future_datetime().replace(tzinfo=pytz.utc)
        self.race.save()
        runs = self.race.populate_runs(self.race_entry_one)
        
        self.assertEqual(len(runs), 12)
        
        for run in Run.objects.filter(status=Run.RUN_STATUS_ASSIGNED):
            self.assertTrue(run.job in self.jobs_first)
        for run in Run.objects.filter(status=Run.RUN_STATUS_PENDING):
            self.assertFalse(run.job in self.jobs_first)
        
    def test_populate_gets_jobs_with_correct_manifest_and_no_manifest(self):
        """i need to get all the shared jobs and/or all the jobs for just my manifest"""
        ### so if everyone is on the same manifest on sunday, we don't blow it
        pass
    
    def test_redo_runs_math(self):
        self.race.race_type=Race.RACE_TYPE_DISPATCH_FINALS
        self.race.race_start_time = fake.future_datetime().replace(tzinfo=pytz.utc)
        self.race.save()
        
        self.race_entry_one = RaceEntryFactory(race=self.race)
        self.race_entry_two = RaceEntryFactory(race=self.race)
        self.race.populate_runs(self.race_entry_one)
        self.race.populate_runs(self.race_entry_two)
        
        first_ready_time = Run.objects.filter(race_entry=self.race_entry_one).first().utc_time_ready
        last_ready_time = Run.objects.filter(race_entry__race=self.race).last().utc_time_ready
        
        self.race.race_start_time += datetime.timedelta(minutes=5)
        self.race.save()
        self.race.redo_run_math()
        
        self.assertTrue(first_ready_time < Run.objects.filter(race_entry__race=self.race).first().utc_time_ready)
        self.assertTrue(first_ready_time < Run.objects.filter(race_entry__race=self.race).last().utc_time_ready)

class ClearRacerTestCase(TestCase):
    def setUp(self):
        right_now = datetime.datetime.now(tz=pytz.utc)
        self.race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH_FINALS, race_start_time=right_now)
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
        """we have a racer that is clear, but they have jobs that are on another dispatcher's screen"""
        
        runs = Run.objects.filter(race_entry=self.race_entry_one)
        runs.delete()
        
        jobs = JobFactory.create_batch(3, race=self.race)
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
        
    def test_dispatch_prelims(self):
        race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH_PRELIMS)
        self.assertTrue(race.dispatch_race)
    
    def test_dispatch_finals(self):
        race = RaceFactory(race_type=Race.RACE_TYPE_DISPATCH_FINALS)
        self.assertTrue(race.dispatch_race)
    
    def test_prelims(self):
        race = RaceFactory(race_type=Race.RACE_TYPE_PRELIMS)
        self.assertFalse(race.dispatch_race)
    
    def test_finals(self):
        race = RaceFactory(race_type=Race.RACE_TYPE_FINALS)
        self.assertFalse(race.dispatch_race)    
        
class ManifestTestCase(TestCase):
    def setUp(self):
        self.manifests = ManifestFactory.create_batch(10)
        
    def test_manifest_type_as_string(self):
        self.manifest = ManifestFactory()
        self.assertTrue(True)