from django.test import TestCase
from .models import Message
from .util import get_next_message
from races.factories import RaceFactory
from .factories import MessageFactory
from raceentries.factories import RaceEntryFactory
import datetime

class get_next_message_TestCase(TestCase):
    def setUp(self):
        self.race = RaceFactory()
        self.race_entry = RaceEntryFactory()
        self.message_one = MessageFactory(race=self.race, race_entry=self.race_entry)
        self.message_two = MessageFactory(race=self.race, race_entry=self.race_entry)
    
    def test_get_next_message_only_does_past_messages(self):
        self.message_one.message_time = datetime.datetime.now() - datetime.timedelta(minutes=2)
        self.message_one.save()
        self.message_two.message_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
        self.message_two.save()
        next_message = get_next_message(self.race)
        self.assertEqual(self.message_one, next_message)
        self.assertNotEqual(self.message_two, next_message)