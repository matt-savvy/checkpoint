from rest_framework.test import APITestCase, APIClient
from rest_framework.test import APIRequestFactory
from races.models import Race
from nacccusers.models import NACCCUser
from checkpoints.models import Checkpoint
from racecontrol.models import RaceControl
from jobs.models import Job
from racers.models import Racer
from runs.models import Run
from raceentries.models import RaceEntry
from raceentries.factories import RaceEntryFactory
import datetime
import pytz
import sys
from time import sleep
from jobs.factories import JobFactory

class RacerCheckpointViewTestCase(APITestCase):
    def setUp(self):
        self.eastern = pytz.timezone('US/Eastern')
        self.now = datetime.datetime.now(tz=self.eastern)
        self.race = Race(race_name='Test Race', race_type=Race.RACE_TYPE_DISPATCH_FINALS, race_start_time=self.now)
        self.race.save()
        self.race_control = RaceControl(current_race=self.race)
        self.race_control.save()
        
        self.pick_checkpoint = Checkpoint(checkpoint_number=1, checkpoint_name="Test Checkpoint 1")
        self.pick_checkpoint.save()
        self.drop_checkpoint = Checkpoint(checkpoint_number=2, checkpoint_name="Test Checkpoint 2")
        self.drop_checkpoint.save()
        self.other_checkpoint = Checkpoint(checkpoint_number=3, checkpoint_name="Test Checkpoint 3")
        self.other_checkpoint.save()
        
        self.checkpoint_worker = NACCCUser()
        self.checkpoint_worker.save()
        self.checkpoint_worker.authorized_checkpoints.add(self.pick_checkpoint)
        self.checkpoint_worker.save()
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.checkpoint_worker)
        
        self.ready_now_job = Job(job_id=1, race=self.race, pick_checkpoint=self.pick_checkpoint, drop_checkpoint=self.drop_checkpoint, minutes_ready_after_start=0)
        self.ready_now_job.save()
        
        self.wrong_checkpoint_job = Job(job_id=2, race=self.race, pick_checkpoint=self.other_checkpoint, drop_checkpoint=self.drop_checkpoint, minutes_ready_after_start=0)
        self.ready_now_job.save()
        
        self.racer = Racer(racer_number=320, first_name='Doug', last_name='Suriano', category=Racer.RACER_CATEGORY_MESSENGER)
        self.racer.save()
            
        self.dq_racer = Racer(racer_number=666, first_name='Doug', last_name='Suriano', category=Racer.RACER_CATEGORY_MESSENGER)
        self.dq_racer.save()
        
        self.dq_entry = RaceEntry(racer=self.dq_racer, race=self.race, entry_status=RaceEntry.ENTRY_STATUS_DQD)
        self.dq_entry.save()
    
        self.raceentry = RaceEntry(racer=self.racer, race=self.race, entry_status=RaceEntry.ENTRY_STATUS_RACING)
        self.raceentry.save()
        
        self.cut_entry = RaceEntryFactory(race=self.race, entry_status=RaceEntry.ENTRY_STATUS_CUT)
        self.cut_entry.save()
        
        self.dnf_entry = RaceEntryFactory(race=self.race, entry_status=RaceEntry.ENTRY_STATUS_DNF)
        self.dnf_entry.save()
        
        self.race.populate_runs(self.raceentry)
        self.race.populate_runs(self.cut_entry)
        self.race.populate_runs(self.dq_entry)
        self.race.populate_runs(self.dnf_entry)
        
    def test_correct_job_available(self):
        runs = Run.objects.filter(race_entry=self.raceentry)
        for run in runs:
            run.status = Run.RUN_STATUS_ASSIGNED
            run.save()
        
        racer_number = str(self.raceentry.racer.racer_number)
        data = {'racer_number' : racer_number, 
                'checkpoint': 1,
        }
        response = self.client.post('/api/v1/racer/', data, format='json')
        self.assertEqual(response.data, self.assertEqual(response.data, {'error' : False, 'error_title' : None, 'error_description' : None, 'available_jobs': None}))
        
class PickTestCase(APITestCase):
    
    def setUp(self):
        self.eastern = pytz.timezone('US/Eastern')
    
        self.now = datetime.datetime.now(tz=self.eastern)
        self.race = Race(race_name='Test Race', race_type=Race.RACE_TYPE_DISPATCH_FINALS, race_start_time=self.now)
        self.race.save()
        self.race_control = RaceControl(current_race=self.race)
        self.race_control.save()
        
        self.pick_checkpoint = Checkpoint(checkpoint_number=1, checkpoint_name="Test Checkpoint 1")
        self.pick_checkpoint.save()
        self.drop_checkpoint = Checkpoint(checkpoint_number=2, checkpoint_name="Test Checkpoint 2")
        self.drop_checkpoint.save()
        self.other_checkpoint = Checkpoint(checkpoint_number=3, checkpoint_name="Test Checkpoint 3")
        self.other_checkpoint.save()
        
        self.ready_now_job = Job(job_id=1, race=self.race, pick_checkpoint=self.pick_checkpoint, drop_checkpoint=self.drop_checkpoint, minutes_ready_after_start=0)
        self.ready_now_job.save()
        
        self.test_minutes_offset = 60
        self.not_ready_job = Job(job_id=2, race=self.race, pick_checkpoint=self.pick_checkpoint, drop_checkpoint=self.drop_checkpoint, minutes_ready_after_start=self.test_minutes_offset)
        self.not_ready_job.save()
        
        self.dead_job = Job(job_id=3, race=self.race, pick_checkpoint=self.pick_checkpoint, drop_checkpoint=self.drop_checkpoint, minutes_ready_after_start=0, minutes_due_after_start=1)
        self.dead_job.save()
        
        self.racer = Racer(racer_number=320, first_name='Doug', last_name='Suriano', category=Racer.RACER_CATEGORY_MESSENGER)
        self.racer.save()
        
        self.dq_racer = Racer(racer_number=666, first_name='Doug', last_name='Suriano', category=Racer.RACER_CATEGORY_MESSENGER)
        self.dq_racer.save()
        
        self.dq_entry = RaceEntry(racer=self.dq_racer, race=self.race, entry_status=RaceEntry.ENTRY_STATUS_DQD)
        self.dq_entry.save()
        
        self.raceentry = RaceEntry(racer=self.racer, race=self.race)
        self.raceentry.save()
        
        self.race.populate_runs(self.raceentry)
        self.race.populate_runs(self.dq_entry)
        
        self.checkpoint_worker = NACCCUser()
        self.checkpoint_worker.save()
        self.checkpoint_worker.authorized_checkpoints.add(self.pick_checkpoint)
        self.checkpoint_worker.save()
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.checkpoint_worker)
        
        
    def test_incorrect_racer_number(self):
        data = {'racer_number' : '999', 
                'checkpoint': 1,
                'run_number' : 1
        }
        response = self.client.post('/api/v1/racer/', data, format='json')
        self.assertEqual(response.data, {'confirm_code' : None, 'error' : True, 'error_title' : 'Cannot Find Racer', 'error_description' : 'No racer found with racer number 999.'})
    
    def test_racer_at_correct_checkpoint(self):
        run = Run.objects.filter(race_entry__racer__racer_number=320).filter(job__job_id=1).first()
        data = {'racer_number' : 320, 
                'checkpoint': 3,
                'run' : run.id,
        }
        response = self.client.post('/api/v1/pick/', data, format='json')
        self.assertEqual(response.data, {'confirm_code' : None, 'error' : True, 'error_title' : 'Wrong Checkpoint', 'error_description' : 'This pick up needs to be made at Test Checkpoint 1.'})
    
    def test_incorrect_job_number(self):
        run = Run.objects.order_by('pk').last()
        run_pk = run.id + 5
        data = {'racer_number' : '320', 
                'checkpoint': 1,
                'run' : run_pk,
        }
        response = self.client.post('/api/v1/pick/', data, format='json')
        self.assertEqual(response.data, {'confirm_code' : None, 'error' : True, 'error_title' : 'Cannot Find Job', 'error_description' : 'No job found.'})
    
    def test_job_is_not_ready(self):
        run = Run.objects.filter(race_entry__racer__racer_number=320).filter(job__job_id=1).first()
        run.utc_time_ready = self.now + datetime.timedelta(minutes=self.test_minutes_offset)
        run.save()
        data = {'racer_number' : 320, 
                'checkpoint': 1,
                'run' : run.id,
        }
        response = self.client.post('/api/v1/pick/', data, format='json')
        test_time = self.now + datetime.timedelta(minutes=self.test_minutes_offset)
        test_time = test_time.astimezone(self.eastern).strftime('%I:%M %p')
        self.assertEqual(response.data, {'confirm_code' : None, 'error' : True, 'error_title' : 'Job is not ready yet.', 'error_description' : 'Job is not ready until {}.'.format(test_time)})
    
    def test_job_is_dead(self):
        run = Run.objects.filter(race_entry__racer__racer_number=320).filter(job__job_id=1).first()
        run.utc_due_time = self.now - datetime.timedelta(minutes=5)
        
        data = {'racer_number' : 320, 
                'checkpoint': 1,
                'run' : run.id,
        }

        response = self.client.post('/api/v1/pick/', data, format='json')
        due_time = self.race.race_start_time.astimezone(pytz.utc) + datetime.timedelta(minutes=self.dead_job.minutes_due_after_start)
        due_time_localized = due_time.astimezone(self.eastern).strftime('%I:%M %p')
        self.assertEqual(response.data, {'confirm_code' : None, 'error' : True, 'error_title' : 'Job is Dead.', 'error_description' : 'Job died at {}.'.format(due_time_localized)})
        
    
    def test_racer_has_done_job(self):
        data = {'racer_number' : '320', 
                'checkpoint': 1,
                'job_number' : 1
        }
        response = self.client.post('/api/v1/pick/', data, format='json')
        confirm_code = response.data['confirm_code']
        response = self.client.post('/api/v1/pick/', data, format='json')
        
        self.assertEqual(response.data, {'confirm_code' : None, 'error' : True, 'error_title' : 'Racer already did job.', 'error_description' : 'The racer has already done job 1, the confirm code was {}'.format(str(confirm_code))})
    
    def test_ok_pick(self):
        data = {'racer_number' : '320', 
                'checkpoint': 1,
                'job_number' : 1
        }
        response = self.client.post('/api/v1/pick/', data, format='json')
        confirm_code = response.data['confirm_code']
        self.assertEqual(response.data, {'confirm_code' : confirm_code, 'error' : False, 'error_title' : None, 'error_description' : None})
        
    def test_racer_dqd(self):
        data = {'racer_number' : '666', 
                'checkpoint': 1,
                'job_number' : 1
        }
        response = self.client.post('/api/v1/pick/', data, format='json')
        confirm_code = response.data['confirm_code']
        self.assertEqual(response.data, {'confirm_code' : None, 'error' : True, 'error_title' : 'Racer has been Disqualified', 'error_description' : 'Race #666 has been disqualified from the race. Have the racer report to HQ if they have any questions.'})
        
class DropTestCase(APITestCase):
    def setUp(self):
        self.eastern = pytz.timezone('US/Eastern')
        self.now = datetime.datetime.now(tz=self.eastern)
        self.race = Race(race_name='Test Race', race_type=Race.RACE_TYPE_FINALS, race_start_time=self.now)
        self.race.save()
        self.race_control = RaceControl(current_race=self.race)
        self.race_control.save()
        
        self.pick_checkpoint = Checkpoint(checkpoint_number=1, checkpoint_name="Test Checkpoint 1")
        self.pick_checkpoint.save()
        self.drop_checkpoint = Checkpoint(checkpoint_number=2, checkpoint_name="Test Checkpoint 2")
        self.drop_checkpoint.save()
        self.other_checkpoint = Checkpoint(checkpoint_number=3, checkpoint_name="Test Checkpoint 3")
        self.other_checkpoint.save()
        
        self.ready_now_job = Job(job_id=1, race=self.race, pick_checkpoint=self.pick_checkpoint, drop_checkpoint=self.drop_checkpoint, minutes_ready_after_start=0)
        self.ready_now_job.save()
                
        self.racer = Racer(racer_number=320, first_name='Doug', last_name='Suriano', category=Racer.RACER_CATEGORY_MESSENGER)
        self.racer.save()
        
        self.raceentry = RaceEntry(racer=self.racer, race=self.race)
        self.raceentry.save()
        
        self.run = Run(pk=1, job=self.ready_now_job, race_entry=self.raceentry, status=Run.RUN_STATUS_PICKED, utc_time_picked=datetime.datetime.now(tz=pytz.utc))
        self.run.save()
    
    def test_not_matching_confirm_code_with_racer(self):
        data = {'racer_number' : 999, 
                'checkpoint': 2,
                'confirm_code' : 1
        }
        response = self.client.post('/api/v1/drop/', data, format='json')
        self.assertEqual(response.data, {'error' : True, 'error_title' : 'Wrong Racer #', 'error_description' : 'Racer # 999 does not a drop off with confirm code 1.'})
    
    def test_incorrect_confirm_code(self):
        data = {'racer_number' : 320, 
                'checkpoint': 2,
                'confirm_code' : 99
        }
        response = self.client.post('/api/v1/drop/', data, format='json')
        self.assertEqual(response.data, {'error' : True, 'error_title' : 'Cannot Find Confirm Code', 'error_description' : "No job's' drop off assoicated with confirm code 99."})
    
    def test_wrong_checkpint(self):
        data = {'racer_number' : 320, 
                'checkpoint': 6,
                'confirm_code' : 1
        }
        response = self.client.post('/api/v1/drop/', data, format='json')
        self.assertEqual(response.data, {'error' : True, 'error_title' : 'Wrong Checkpoint', 'error_description' : 'This drop off needs to be made at Test Checkpoint 2.'})
    
    def test_racer_already_dropped_off(self):
        data = {'racer_number' : 320, 
                'checkpoint': 2,
                'confirm_code' : 1
        }
        response = self.client.post('/api/v1/drop/', data, format='json')
        drop_time = datetime.datetime.now(tz=self.eastern).strftime('%I:%M %p')
        response = self.client.post('/api/v1/drop/', data, format='json')
        self.assertEqual(response.data, {'error' : True, 'error_title' : 'Job already dropped off', 'error_description' : 'The run was already dropped off at {}.'.format(drop_time)})
    
    def test_ok_drop(self):
        data = {'racer_number' : 320, 
                'checkpoint': 2,
                'confirm_code' : 1
        }
        response = self.client.post('/api/v1/drop/', data, format='json')
        self.assertEqual(response.data, {'error' : False, 'error_title' : None, 'error_description' : None})