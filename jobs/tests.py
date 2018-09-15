from django.test import TestCase
from .models import Job
from .factories import JobFactory

class JobTestCase(TestCase):
    def test_service_string_regular(self):
        job = JobFactory(minutes_due_after_start=6666)
        self.assertEqual(job.service, "REGULAR")
        
    def test_service_string_rush(self):
        job = JobFactory(minutes_due_after_start=15)
        self.assertEqual(job.service, "RUSH")
        
    def test_service_string_double_rush(self):
        job = JobFactory(minutes_due_after_start=7)
        self.assertEqual(job.service, "DOUBLE RUSH")