from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
from checkpoints.models import Checkpoint
import random
import itertools


def random_permutation(iterable, r=2):
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))

class Command(BaseCommand):
   
   

   
   
   def handle(self, *args, **options):
       races = Race.objects.order_by('pk')
       for race in races:
           print "{} {}".format(race.pk, race)
           
       
       
       selection_race = int(raw_input("choose race number : "))
       
       for manifest in Manifest.objects.all():
           print "{} {}".format(manifest.pk, manifest)
           
       selection_manifest = int(raw_input("choose manifest number : "))
       selection_number_of_jobs = int(raw_input("number of jobs: "))
       
       race = Race.objects.get(pk=selection_race)
       checkpoints = Checkpoint.objects.all()
       manifest = Manifest.objects.get(pk=selection_manifest)
       #TODO add filter for removing HQ so we don't overdo that checkpoint
       
       
       all_jobs = []
       
       import pdb
       
       checkpoint_combos = itertools.permutations(checkpoints, 2)
       checkpoint_combos_list = random_permutation(checkpoint_combos, selection_number_of_jobs)
       
       #pdb.set_trace()
       
       job_counter = 0
       try:
           job_id = Job.objects.all().order_by('job_id').last().job_id
       except:
           job_id = 0
       minutes_counter = 0
       while job_counter < selection_number_of_jobs:
           jobs_in_this_set = random.randint(1,4)
           random_minutes = random.randint(5,14)
           this_set_counter = 0
           minutes_counter += random_minutes
           while this_set_counter <= jobs_in_this_set:
               checkpoint_combo = checkpoint_combos_list[job_counter]
               job_id += 1
               
               job = Job(job_id=job_id, race=race, pick_checkpoint=checkpoint_combo[0], drop_checkpoint=checkpoint_combo[1], minutes_ready_after_start=minutes_counter)
               random_number = random.random()
               if random_number >= .9:
                   job.minutes_due_after_start = Job.SERVICE_DOUBLE_RUSH
                   job.points = Job.PAYOUT_DOUBLE_RUSH
               elif random_number >= .6:
                   job.minutes_due_after_start = Job.SERVICE_RUSH
                   job.points = Job.PAYOUT_RUSH
               else:
                   job.minutes_due_after_start = Job.SERVICE_REGULAR
                   job.points = Job.PAYOUT_REGULAR
               
               job.manifest = manifest
               job.save()
               
               this_set_counter += 1
               job_counter += 1
       
       print "{} jobs created.".format(job_counter)