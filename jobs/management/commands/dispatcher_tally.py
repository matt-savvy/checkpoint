from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
from dispatch.models import Message
from runs.models import Run
from racers.models import Racer
from raceentries.models import RaceEntry
from checkpoints.models import Checkpoint
from django.db.models import Q
import decimal
import random
import itertools
import datetime
import pytz
import pdb
from dispatch.util import simulate_race
from racelogs.models import RaceLog
from freezegun import freeze_time
from nacccusers.models import NACCCUser

class Command(BaseCommand):
    def handle(self, *args, **options):
        dispatchers = NACCCUser.objects.all()
        for dispatcher in dispatchers:
            dispatcher.tally = 0
        
        logs = RaceLog.objects.filter(race__pk=2).filter(log__contains="Racer confirmed message ")
        for log in logs:
            pk = log.log.split("Racer confirmed message ")[1]
            pk = pk.split(".")[0]
            message = Message.objects.filter(pk=pk).first()
            if message:
                dispatcher = log.user
                run_count = message.runs.count()
                dispatcher.tally =+ run_count

        for dispatcher in dispatchers:
            print dispatcher, dispatcher.tally