from django.test import TestCase
from .models import Message
from runs.models import Run
from races.models import Race, Manifest
from raceentries.models import RaceEntry
from .util import get_next_message
from jobs.factories import JobFactory
from races.factories import RaceFactory, ManifestFactory
from .factories import MessageFactory
from raceentries.factories import RaceEntryFactory
from runs.factories import RunFactory
import datetime
import pytz
import pdb
from django.conf import settings
from django.db.models import Q

class MessageTestCase(TestCase):
    def setUp(self):
        right_now = datetime.datetime.now(tz=pytz.utc)
        self.race = RaceFactory(race_start_time=right_now, race_type=Race.RACE_TYPE_DISPATCH)
        self.race_entry = RaceEntryFactory(race=self.race)
        self.jobs = JobFactory.create_batch(3, race=self.race, minutes_ready_after_start=0)
        self.runs_one = self.race.populate_runs(self.race_entry)
        
    def test_unicode_dispatch_with_runs(self):
        message = Message(race=self.race, race_entry=self.race_entry, message_type=Message.MESSAGE_TYPE_DISPATCH)
        message.save()
        for run in Run.objects.all():
            message.runs.add(run)

        self.assertTrue("assign runs" in message.__unicode__())
    
    def test_unicode_office(self):
        message = Message(race=self.race, race_entry=self.race_entry, message_type=Message.MESSAGE_TYPE_OFFICE)

        self.assertTrue("Come to the Office" in message.__unicode__())
        
    def test_unicode_error(self):
        message = Message(race=self.race, race_entry=self.race_entry, message_type=Message.MESSAGE_TYPE_ERROR)

        self.assertTrue("ERROR" in message.__unicode__())
        
    def test_unicode_nothing(self):
        message = Message(race=self.race, message_type=Message.MESSAGE_TYPE_NOTHING)

        self.assertTrue("Blank Message" in message.__unicode__())
        
    def test_confirm_message(self):
        self.race_entry.entry_status = RaceEntry.ENTRY_STATUS_RACING
        self.race_entry.save()
        message = Message(race=self.race, race_entry=self.race_entry, message_type=Message.MESSAGE_TYPE_DISPATCH)
        message.save()
        for run in Run.objects.all():
            message.runs.add(run)
            
        message.confirm()
        self.assertEqual(message.runs.first().status, Run.RUN_STATUS_ASSIGNED)
        self.assertEqual(message.status, Message.MESSAGE_STATUS_CONFIRMED)
        
    def test_confirm_cut(self):
        self.race_entry.entry_status = RaceEntry.ENTRY_STATUS_RACING
        self.race_entry.save()
        message = Message(race=self.race, race_entry=self.race_entry, message_type=Message.MESSAGE_TYPE_OFFICE)
        message.save()
            
        message.confirm()
        race_entry = RaceEntry.objects.get(pk=self.race_entry.pk)
        self.assertEqual(race_entry.entry_status, RaceEntry.ENTRY_STATUS_CUT)
        self.assertEqual(message.status, Message.MESSAGE_STATUS_CONFIRMED)
        
class get_next_message_TestCase(TestCase):
    def setUp(self):
        right_now = datetime.datetime.now(tz=pytz.utc)
        self.race = RaceFactory(race_start_time=right_now, race_type=Race.RACE_TYPE_DISPATCH)
        self.race_entry = RaceEntryFactory(race=self.race)
        self.jobs_first = JobFactory.create_batch(3, race=self.race, minutes_ready_after_start=0)
        self.jobs_second = JobFactory.create_batch(3, race=self.race, minutes_ready_after_start=10)
        self.race_entry_one = RaceEntryFactory(race=self.race, entry_status=RaceEntry.ENTRY_STATUS_ENTERED)
        self.race_entry_one.start_racer()
        self.race_entry_two = RaceEntryFactory(race=self.race, entry_status=RaceEntry.ENTRY_STATUS_ENTERED)
        self.race_entry_two.start_racer()
        self.runs_one = self.race.populate_runs(self.race_entry_one)
        self.runs_two = self.race.populate_runs(self.race_entry_two)
        
    def test_race_has_started(self):
        right_now = datetime.datetime.now(tz=pytz.utc)
        self.race = RaceFactory(race_start_time=right_now + datetime.timedelta(minutes=60))
        next_message = get_next_message(self.race)
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_ERROR)
        
    def test_get_next_message_only_does_past_messages(self):
        message_one = MessageFactory(race=self.race, race_entry=self.race_entry)
        message_one.message_time = datetime.datetime.now() - datetime.timedelta(minutes=2)
        message_one.save()
        message_two = MessageFactory(race=self.race, race_entry=self.race_entry)
        message_two.message_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
        message_two.save()
        next_message = get_next_message(self.race)
        self.assertEqual(message_one, next_message)
        self.assertNotEqual(message_two, next_message)
    
    def test_get_next_message_message_snoozed(self):
        """make sure a snoozed job goes back in the queue """
        right_now = datetime.datetime.now(tz=pytz.utc)
        message_one = MessageFactory(race=self.race, race_entry=self.race_entry_one, message_time=right_now)
        
        message_one.snooze()
        
        messages = Message.objects.filter(race=self.race).filter(status=Message.MESSAGE_STATUS_SNOOZED)
        
        self.assertTrue(message_one in messages)
    
    def test_snooze_delays_a_message(self):
        """make sure when we hit snooze it will get bumped back a good sixty seconds"""
        right_now = datetime.datetime.now(tz=pytz.utc)
        message_one = MessageFactory(race=self.race, race_entry=self.race_entry_one, message_time=right_now)
        
        message_one.snooze()
        
        messages = Message.objects.filter(race=self.race).filter(status=Message.MESSAGE_STATUS_SNOOZED)
        Message.objects.exclude(pk=message_one.pk).all().delete()
        next_message = get_next_message(self.race)
        
        self.assertNotEqual(next_message.runs, message_one.runs)
        
    def test_get_next_message_gets_a_snoozed_message(self):
        """make sure a snoozed job goes back in the queue """
        five_mins_ago = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(seconds=75)
        message_one = MessageFactory(race=self.race, race_entry=self.race_entry_one, message_time=five_mins_ago, status=Message.MESSAGE_STATUS_SNOOZED)
        
        next_message = get_next_message(self.race)
        
        self.assertEqual(message_one, next_message)
        
    def test_get_next_message_no_messages_but_jobs(self):
        """no messages in the queue but we got some jobs to dispatch"""
        next_message = get_next_message(self.race)
        next_message_runs = next_message.runs.all()
        
        for job in self.jobs_first:
            run = Run.objects.filter(job=job).first()
            self.assertTrue(run in next_message_runs)
    
    def test_cut_racers_that_know_it_dont_get_told_it_repeatedly(self):
        """if you're cut, you get told once, confirm it, and that's it"""

        racer = self.race.find_clear_racer()
        race_entries = RaceEntry.objects.exclude(pk=racer.pk)
        race_entries.delete()        
        Run.objects.all().delete()
        racer.entry_status = RaceEntry.ENTRY_STATUS_CUT
        racer.save()
        message = Message(race_entry=racer, race=racer.race, message_type=Message.MESSAGE_TYPE_OFFICE, status=Message.MESSAGE_STATUS_CONFIRMED)
        message.save()
        next_message = get_next_message(self.race)

        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_NOTHING)
        
    
    
    def test_no_double_messages_for_racer(self):
        """only message is a message already on a screen, next_message() should return a NOTHING message"""
        messages = Message.objects.all().delete()
        runs = Run.objects.all()
        for run in runs:
            run.status = Run.RUN_STATUS_COMPLETED
            run.save()
        
        message = Message(race=self.race_entry_one.race, race_entry=self.race_entry_one, message_type=Message.MESSAGE_TYPE_OFFICE, status=Message.MESSAGE_STATUS_DISPATCHING)
        message.save()
        
        next_message = get_next_message(self.race)

        self.assertNotEqual(next_message.race_entry, self.race_entry_one)
        
    def test_message_left_unconfirmed_for_too_long_gets_attempted_again(self):
        first_next_message = get_next_message(self.race)
        first_next_message_pk = first_next_message.pk
        first_next_message.message_time = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(minutes=5)
        first_next_message.save()
        
        next_message = get_next_message(self.race)
        self.assertEqual(next_message.pk, first_next_message.pk)
        
           
    def test_get_next_message_runs_with_no_ready_time(self):
        """make sure if a job has no ready time, we act like it's ready now"""
        racer = self.race.find_clear_racer()
        no_time_ready_run = Run.objects.filter(race_entry=racer).last()
        no_time_ready_run.utc_time_ready = None
        no_time_ready_run.save()
  
        next_message = get_next_message(self.race)
        next_message_runs = next_message.runs.all()
        
        self.assertTrue(no_time_ready_run in next_message_runs)
    
    def test_clear_racer_with_no_pending_jobs(self):
        "a clear racer with no pending jobs should be told to come back to the office because there is no bonus manifest"
        racer = self.race.find_clear_racer()
        runs = Run.objects.filter(race_entry=racer)
        runs.delete()
        
        next_message = get_next_message(self.race)
        next_message_runs = next_message.runs.all()
        
        self.assertIsNone(next_message_runs.first())
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_OFFICE)
    
    def test_clear_racer_with_no_pending_jobs_but_bonus_manifest_exists(self):
        "a clear racer with no pending jobs should be given work from the bonus manifest"
        racer = self.race.find_clear_racer()
        runs = Run.objects.filter(race_entry=racer)
        runs.delete()
        
        bonus_manifest = ManifestFactory(race=self.race, manifest_type=Manifest.TYPE_CHOICE_BONUS)
        job = JobFactory(race=self.race, manifest=bonus_manifest)
        
        next_message = get_next_message(self.race)
        next_message_runs = next_message.runs.all()
        
        first_run = next_message_runs[0]
        self.assertEqual(first_run.job, job)
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_DISPATCH)
        
    def test_clear_racer_with_no_pending_jobs_bonus_manifest_exists_before_cut_off_time(self):
        "a clear racer with no pending jobs should be given work from the bonus manifest because we are well before the cut off time"
        racer = self.race.find_clear_racer()
        runs = Run.objects.filter(race_entry=racer)
        runs.delete()
        
        bonus_manifest = ManifestFactory(race=self.race, manifest_type=Manifest.TYPE_CHOICE_BONUS, cut_off_minutes_after_start=20)
        self.race.start_time = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(minutes=10)
        job = JobFactory(race=self.race, manifest=bonus_manifest)
        
        next_message = get_next_message(self.race)
        first_run = next_message.runs.first()
        
        self.assertEqual(first_run.job, job)
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_DISPATCH)
        
    def test_clear_racer_with_no_pending_jobs_bonus_manifest_exists_after_cut_off_time(self):
        "a clear racer with no pending jobs should be cut because we are after the bonus cut off time. they should also get cut"
        racer = self.race.find_clear_racer()
        runs = Run.objects.filter(race_entry=racer)
        runs.delete()
        
        bonus_manifest = ManifestFactory.create(race=self.race, manifest_type=Manifest.TYPE_CHOICE_BONUS, cut_off_minutes_after_start=20)
        self.race.race_start_time = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(minutes=30)
        self.race.save()
        
        job = JobFactory.create(race=self.race, manifest=bonus_manifest)
        
        next_message = get_next_message(self.race)
        racer = RaceEntry.objects.get(pk=racer.pk)
        
        self.assertIsNone(next_message.runs.first())
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_OFFICE)
        self.assertEqual(racer.entry_status, RaceEntry.ENTRY_STATUS_CUT)
        
    def test_clear_racer_with_no_pending_jobs_bonus_manifest_exists_but_all_jobs_done(self):
        "a clear racer with no pending jobs who also did all the bonus jobs. they should get cut"
        racer = self.race.find_clear_racer()
        runs = Run.objects.filter(race_entry=racer)
        runs.delete()
        
        bonus_manifest = ManifestFactory(race=self.race, manifest_type=Manifest.TYPE_CHOICE_BONUS, cut_off_minutes_after_start=20)
        self.race.start_time = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(minutes=10)
        job = JobFactory(race=self.race, manifest=bonus_manifest)
        run = RunFactory(job=job, race_entry=racer, status=Run.RUN_STATUS_COMPLETED)
        
        next_message = get_next_message(self.race)
        racer = RaceEntry.objects.get(pk=racer.pk)
        
        self.assertIsNone(next_message.runs.first())
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_OFFICE)
        self.assertEqual(racer.entry_status, RaceEntry.ENTRY_STATUS_CUT)
        
    def test_get_next_message_with_two_sets_of_runs_ready_now(self):
        """some of these jobs was ready 5 mins ago, some were ready 8 mins ago. we should get them all back"""
        runs = Run.objects.filter(race_entry=self.race_entry_one)
        right_now = datetime.datetime.now(tz=pytz.utc) 
        
        runs[0].utc_time_ready = right_now - datetime.timedelta(minutes=5)
        runs[0].save()
        runs[1].utc_time_ready = right_now - datetime.timedelta(minutes=5)
        runs[1].save()
        runs[2].utc_time_ready = right_now - datetime.timedelta(minutes=10)
        runs[2].save()
        
        next_message = get_next_message(self.race)
        next_message_runs = next_message.runs.all()
        
        for run in runs:
            self.assertTrue(run in next_message_runs)
    
    def test_no_messages_or_jobs(self):
        """make sure we got a MESSAGE_TYPE_NOTHING"""
        Run.objects.all().delete()
        Message.objects.all().delete()
        
        self.race_entry_one.entry_status = RaceEntry.ENTRY_STATUS_FINISHED
        
        self.race_entry_two.entry_status = RaceEntry.ENTRY_STATUS_DQD
        self.race_entry_one.save()
        self.race_entry_two.save()
        next_message = get_next_message(self.race)
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_NOTHING)
        
        self.race_entry_one.entry_status = RaceEntry.ENTRY_STATUS_DNF
        self.race_entry_two.entry_status = RaceEntry.ENTRY_STATUS_PROCESSING
        self.race_entry_one.save()
        self.race_entry_two.save()
        next_message = get_next_message(self.race)
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_NOTHING)
        
        self.race_entry_one.entry_status = RaceEntry.ENTRY_STATUS_ENTERED
        self.race_entry_one.save()
        self.race_entry_two.save()
        next_message = get_next_message(self.race)
        self.assertEqual(next_message.message_type, Message.MESSAGE_TYPE_NOTHING)
    
    def test_get_next_message_no_messages_but_clear_racer(self):
        """no messages in the queue but we got a clear racer with pending work"""
        runs = Run.objects.filter(utc_time_ready__lte=self.race.race_start_time)
        runs.filter(race_entry=self.race_entry_one).delete()
        runs.filter(race_entry=self.race_entry_two).first().assign()
        
        ##so we got runs for racer two ready now and runs for racer one ready in ten, but racer one is clear!
        next_message = get_next_message(self.race)
        self.assertEqual(next_message.race_entry, self.race_entry_one)
        
        for run in next_message.runs.all():
            self.assertTrue(run in Run.objects.filter(race_entry=self.race_entry_one))
    
    def test_get_next_message_when_rider_has_more_than_13_assigned_jobs(self):
        Run.objects.all().delete()
        right_now = datetime.datetime.now(tz=pytz.utc) 
        RaceEntry.objects.exclude(pk=self.race_entry_one.pk).all().delete()
        runs = RunFactory.create_batch(settings.OPEN_RUN_LIMIT, race_entry=self.race_entry_one, status=Run.RUN_STATUS_ASSIGNED)
        last_run = RunFactory(race_entry=self.race_entry_one, status=Run.RUN_STATUS_PENDING, utc_time_ready=right_now)
        
        next_message = get_next_message(self.race)
        print last_run
        print next_message
        self.assertFalse(last_run in next_message.runs.all())
        self.assertNotEqual(next_message.race_entry, self.race_entry_one)
    
    def test_get_next_message_when_rider_has_more_than_13_picked_jobs(self):
        Run.objects.all().delete()
        right_now = datetime.datetime.now(tz=pytz.utc) 
        RaceEntry.objects.exclude(pk=self.race_entry_one.pk).all().delete()
        runs = RunFactory.create_batch(settings.OPEN_RUN_LIMIT, race_entry=self.race_entry_one, status=Run.RUN_STATUS_PICKED)
        last_run = RunFactory(race_entry=self.race_entry_one, status=Run.RUN_STATUS_PENDING, utc_time_ready=right_now)
        
        next_message = get_next_message(self.race)
        print last_run
        print next_message
        self.assertFalse(last_run in next_message.runs.all())
        self.assertNotEqual(next_message.race_entry, self.race_entry_one)
    
    def test_get_next_message_when_rider_has_more_than_13_assigned_or_picked_jobs(self):
        Run.objects.all().delete()
        right_now = datetime.datetime.now(tz=pytz.utc) 
        RaceEntry.objects.exclude(pk=self.race_entry_one.pk).all().delete()
        RunFactory.create_batch(6, race_entry=self.race_entry_one, status=Run.RUN_STATUS_ASSIGNED)
        RunFactory.create_batch(7, race_entry=self.race_entry_one, status=Run.RUN_STATUS_PICKED)
        last_run = RunFactory(race_entry=self.race_entry_one, status=Run.RUN_STATUS_PENDING, utc_time_ready=right_now)
        
        next_message = get_next_message(self.race)
        print last_run
        print next_message
        self.assertFalse(last_run in next_message.runs.all())
        self.assertNotEqual(next_message.race_entry, self.race_entry_one)
        
    def test_get_next_message_when_rider_has_plenty_of_completed_jobs(self):
        Run.objects.all().delete()
        right_now = datetime.datetime.now(tz=pytz.utc) 
        RaceEntry.objects.exclude(pk=self.race_entry_one.pk).all().delete()
        RunFactory.create_batch(6, race_entry=self.race_entry_one, status=Run.RUN_STATUS_ASSIGNED)
        RunFactory.create_batch(13, race_entry=self.race_entry_one, status=Run.RUN_STATUS_COMPLETED)
        last_run = RunFactory(race_entry=self.race_entry_one, status=Run.RUN_STATUS_PENDING, utc_time_ready=right_now)
        
        next_message = get_next_message(self.race)
        print last_run
        print next_message
        self.assertTrue(last_run in next_message.runs.all())
    
    def test_get_next_message_when_rider_will_pass_open_job_limit(self):
        """we'll set them at 10 jobs and make sure that even though there are 5 that are pending for him coming up, we only give him 3 more"""
        Run.objects.all().delete()
        right_now = datetime.datetime.now(tz=pytz.utc) 
        RaceEntry.objects.exclude(pk=self.race_entry_one.pk).all().delete()
        RunFactory.create_batch(5, race_entry=self.race_entry_one, status=Run.RUN_STATUS_ASSIGNED)
        RunFactory.create_batch(5, race_entry=self.race_entry_one, status=Run.RUN_STATUS_PICKED)
        last_possible_runs = RunFactory.create_batch(5, race_entry=self.race_entry_one, status=Run.RUN_STATUS_PENDING, utc_time_ready=right_now)
        very_last_runs = last_possible_runs[:3]

        denied_last_runs = last_possible_runs[3:5]
        
        next_message = get_next_message(self.race)
        
        self.assertEqual(Run.objects.filter(race_entry=self.race_entry_one).exclude(status=Run.RUN_STATUS_PENDING).count(), settings.OPEN_RUN_LIMIT)
        
        for run in very_last_runs:
            self.assertTrue(run in next_message.runs.all())
            
        for run in denied_last_runs:
            self.assertFalse(run in next_message.runs.all())
        
        ##make sure we
        #only get jobs for the correct racer
        #only get jobs that are not already assigned, picked, or complete
        #are we getting them in correct order of starting position?