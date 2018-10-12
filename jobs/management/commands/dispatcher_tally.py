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
        chris49 = NACCCUser.objects.get(pk=7)
        chris49.tally = 0
        dave = NACCCUser.objects.get(pk=20)
        dave.tally = 0
        doug = NACCCUser.objects.get(pk=12)
        doug.tally = 0
        hank = NACCCUser.objects.get(pk=6)
        hank.tally = 0
        jessie = NACCCUser.objects.get(pk=8)
        jessie.tally = 0
        magic = NACCCUser.objects.get(pk=4)
        magic.tally = 0
        matt = NACCCUser.objects.get(pk=1)
        matt.tally = 0
        baj = NACCCUser.objects.get(pk=2)
        baj.tally = 0
        dispatchers = [chris49, dave, doug, hank, jessie, magic, matt, baj]
        logs = RaceLog.objects.filter(race__pk=2).filter(log__contains="Racer confirmed message ")
        for log in logs:
            pk = log.log.split("Racer confirmed message ")[1]
            pk = pk.split(".")[0]
            message = Message.objects.filter(pk=pk).first()
            if message:
                run_count = message.runs.count()
                dispatcher = log.user
                if dispatcher == chris49:
                    chris49.tally += run_count
                elif dispatcher == dave:
                    dave.tally += run_count
                elif dispatcher == doug:
                    doug.tally += run_count
                elif dispatcher == hank:
                    hank.tally += run_count
                elif dispatcher == jessie:
                    jessie.tally += run_count
                elif dispatcher == magic:
                    magic.tally += run_count
                elif dispatcher == magic:
                    magic.tally += run_count
                elif dispatcher == matt:
                    matt.tally += run_count
                elif dispatcher == baj:
                    baj.tally += run_count
                
                dispatcher.tally =+ run_count

        for dispatcher in dispatchers:
            print dispatcher, dispatcher.tally