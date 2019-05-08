from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
from dispatch.models import Message
from runs.models import Run
from racers.models import Racer
from raceentries.models import RaceEntry
from racecontrol.models import RaceControl
from companies.models import Company
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

        companies = Company.objects.all()
        for company in companies:
            if company.get_racers():
                if CompanyEntry.objects.filter(race=race).filter(company=company).exists():
                    print("{} - CompanyEntry.exists()".format(company.name))
                else:
                    company_entry = CompanyEntry(race=race, company=company)
                    company_entry.save()
                    print("{} - CompanyEntry created!".format(company.name))
            else:
                print("{} - No racers found!".format(company.name))
