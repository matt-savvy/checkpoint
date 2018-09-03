from django.test import TestCase
from .models import Message
from runs.models import Run
from races.models import Race
from raceentries.models import RaceEntry
from .util import get_next_message
from jobs.factories import JobFactory
from races.factories import RaceFactory
from .factories import MessageFactory
from raceentries.factories import RaceEntryFactory
import datetime
import pytz

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
        message_two = MessageFactory(race=self.race, race_entry=self.race_entry_two, message_time=right_now)
        
        message_one.snooze()
        
        next_message = get_next_message(self.race)
        self.assertEqual(message_two, next_message)
        
        messages = Message.objects.filter(race=self.race).filter(confirmed=False)
        self.assertTrue(message_one in messages)
        
    def test_get_next_message_no_messages_but_jobs(self):
        """no messages in the queue but we got some jobs to dispatch"""
        next_message = get_next_message(self.race)
        next_message_runs = next_message.runs.all()
        
        for job in self.jobs_first:
            run = Run.objects.filter(job=job).first()
            self.assertTrue(run in next_message_runs)
    
    def test_get_next_message_no_messages_but_clear_racer(self):
        """no messages in the queue but we got some jobs to dispatch"""
        next_message = get_next_message(self.race)
        next_message_runs = next_message.runs.all()
        
        for job in self.jobs_first:
            run = Run.objects.filter(job=job).first()
            self.assertTrue(run in next_message_runs)
    
    
    
        
        ##make sure we
        #only get jobs for the correct racer
        #only get jobs that are not already assigned, picked, or complete
        #are we getting them in correct order of starting position?