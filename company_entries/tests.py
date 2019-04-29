from django.test import TestCase
from .factories import CompanyEntryFactory
from .models import CompanyEntry
from companies.factories import CompanyFactory
from raceentries.factories import RaceEntryFactory
from raceentries.models import RaceEntry
from races.factories import RaceFactory
from runs.models import Run
from jobs.factories import JobFactory
import decimal

class CompanyEntryTestCase(TestCase):
    def setUp(self):
        self.race = RaceFactory()
        self.company_one = CompanyFactory()
        self.racers_one = RaceEntryFactory.create_batch(3, race=self.race, racer__company=self.company_one)
        self.company_entry_one = CompanyEntryFactory(company=self.company_one, race=self.race)

        self.company_two = CompanyFactory()
        self.racers_two = RaceEntryFactory.create_batch(3, race=self.race, racer__company=self.company_two)
        self.company_entry_two = CompanyEntryFactory(company=self.company_two, race=self.race)

    def test_get_race_entries(self):
        entries = self.company_entry_one.get_race_entries()

        for entry in self.racers_one:
            self.assertIn(entry, entries)
        for entry in self.racers_two:
            self.assertNotIn(entry, entries)

    def test_populate_runs(self):
        jobs = JobFactory.create_batch(20, race=self.race)
        self.company_entry_one.populate_runs()
        run_count = Run.objects.filter(company_entry=self.company_entry_one).filter(status=Run.RUN_STATUS_PENDING).count()
        self.assertEqual(run_count, 20)

    def test_start_racers_populates_jobs(self):
        jobs = JobFactory.create_batch(20, race=self.race)
        self.company_entry_one.start_racers()
        run_count = Run.objects.filter(company_entry=self.company_entry_one).count()
        self.assertEqual(run_count, 20)

    def test_start_racers_starts_all_racers(self):
        self.company_entry_one.start_racers()
        for entry in self.racers_one:
            entry = RaceEntry.objects.get(pk=entry.pk)
            self.assertEqual(entry.entry_status, RaceEntry.ENTRY_STATUS_RACING)
            self.assertEqual(entry.points_earned, decimal.Decimal('0.00'))
            self.assertEqual(entry.deductions, decimal.Decimal('0.00'))
            self.assertEqual(entry.grand_total, decimal.Decimal('0.00'))
        for entry in self.racers_two:
            self.assertEqual(entry.entry_status, RaceEntry.ENTRY_STATUS_ENTERED)

    def test_start_racers_updates_company_entry_status(self):
        self.company_entry_one.start_racers()
        self.assertEqual(self.company_entry_one.entry_status, CompanyEntry.ENTRY_STATUS_RACING)

    def test_finish_racers(self):
        self.company_entry_one.start_racers()
        self.company_entry_one.finish_racers()
        for entry in self.racers_one:
            entry = RaceEntry.objects.get(pk=entry.pk)
            self.assertEqual(entry.entry_status, RaceEntry.ENTRY_STATUS_FINISHED)
        for entry in self.racers_two:
            self.assertEqual(entry.entry_status, RaceEntry.ENTRY_STATUS_ENTERED)

    def test_finish_racers_updates_company_entry_status(self):
        self.company_entry_one.finish_racers()
        self.assertEqual(self.company_entry_one.entry_status, CompanyEntry.ENTRY_STATUS_FINISHED)

    def test_unstart_racers_resets_status_and_points(self):
        self.company_entry_one.start_racers()
        self.company_entry_one.unstart_racers()
        for entry in self.racers_one:
            entry = RaceEntry.objects.get(pk=entry.pk)
            self.assertEqual(entry.entry_status, RaceEntry.ENTRY_STATUS_ENTERED)

    def test_unstart_racers_updates_company_entry_status(self):
        self.company_entry_one.start_racers()
        self.company_entry_one.unstart_racers()
        self.assertEqual(self.company_entry_one.entry_status, CompanyEntry.ENTRY_STATUS_ENTERED)

    def test_unstart_racers_deletes_all_runs(self):
        self.company_entry_one.start_racers()
        self.company_entry_two.start_racers()
        self.company_entry_one.unstart_racers()
        run_count = Run.objects.filter(company_entry=self.company_entry_one).count()
        self.assertEqual(run_count, 0)
