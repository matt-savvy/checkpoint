from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
from dispatch.models import Message
from runs.models import Run
from racers.models import Racer
from raceentries.models import RaceEntry
from racecontrol.models import RaceControl
from company_entries.models import CompanyEntry
from checkpoints.models import Checkpoint
from django.db.models import Q
import decimal
import random
import itertools
import datetime
import pytz
import pdb
from dispatch.util import simulate_race
from freezegun import freeze_time

class Command(BaseCommand):
    def handle(self, *args, **options):
        races = Race.objects.order_by('pk')
        for race in races:
            print "{} {}".format(race.pk, race)
        selection_race = int(raw_input("choose race number : "))

        race = Race.objects.get(pk=selection_race)

        rc = RaceControl.shared_instance()
        if rc.current_race == race:
            rc.racers_started = False
            rc.save()

        runs = Run.objects.filter(company_entry__race=race)
        runs.delete()

        race_entries = RaceEntry.objects.filter(race=race)
        race_entries.update(entry_status=RaceEntry.ENTRY_STATUS_ENTERED, start_time=None)

        company_entries = CompanyEntry.objects.filter(race=race)
        company_entries.update(entry_status=CompanyEntry.ENTRY_STATUS_ENTERED, start_time=None)
