from django.test import TestCase
from racers.factories import RacerFactory
from companies.factories import CompanyFactory
from nacccusers.factories import NACCCUserFactory

class CompanyTestCase(TestCase):
    def setUp(self):
        self.user = NACCCUserFactory()
        self.company = CompanyFactory(dispatcher=self.user)
        self.company_racers = RacerFactory.create_batch(3, company=self.company)

    def test_get_racers(self):
        racers = self.company.get_racers()
        for racer in self.company_racers:
            self.assertIn(racer, racers)

    def test_other_racer_not_in_get_racers(self):
        racers = self.company.get_racers()
        other_user = NACCCUserFactory(username="whatever")
        other_company = CompanyFactory(dispatcher=other_user)
        other_racer = RacerFactory()
        self.assertIn(other_racer, racers)
