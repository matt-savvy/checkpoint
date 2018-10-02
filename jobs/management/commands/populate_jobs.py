from django.core.management.base import BaseCommand, CommandError
from jobs.models import Job
from races.models import Race, Manifest
from django.db.models import Count
from checkpoints.models import Checkpoint
import random
import itertools
from jobs.factories import JobFactory

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
        
        
        #race = Race.objects.get(pk=1)
        #manifest = None
        #selection_number_of_jobs = 40
        
        selection_race = int(raw_input("choose race number : "))
        race = Race.objects.get(pk=selection_race)
       
        for manifest in Manifest.objects.filter(race=race).all():
            print "{} {}".format(manifest.pk, manifest)
           
        selection_manifest = int(raw_input("choose manifest number or 0 for None: "))
        selection_number_of_jobs = int(raw_input("number of jobs total jobs: "))
       
        checkpoints = Checkpoint.objects.all()
        if selection_manifest == 0:
            manifest = None
        else:
            manifest = Manifest.objects.get(pk=selection_manifest)       
       

        import pdb

        #checkpoint_combos = itertools.permutations(checkpoints, 2)
        #checkpoint_combos_list = random_permutation(checkpoint_combos, selection_number_of_jobs)
       
        job_counter = 0
        job_id = Job.objects.all().order_by('job_id').last().job_id + 1

        minutes_counter = 0
       
        most_picked_checkpoint = None
        most_dropped_checkpoint = None
        least_picked_checkpoint = None
        least_dropped_checkpoint = None
       
        while job_counter < selection_number_of_jobs:
            this_set_counter = 0
            try:
                jobs_in_this_set = int(raw_input("number of jobs in this set: "))
            except:
                jobs_in_this_set = 3
            try:  
                minutes_since_last_set = int(raw_input("minutes since last set: "))
            except:
                minutes_since_last_set = 12
                
            minutes_counter += minutes_since_last_set
            print "{} ready at {} minutes:".format(jobs_in_this_set, minutes_since_last_set)
            
            checkpoints = Checkpoint.objects.all()
            
            while this_set_counter < jobs_in_this_set:
                
                this_race_jobs = Job.objects.filter(race=race)

                for checkpoint in checkpoints:
                    checkpoint.num_picks = this_race_jobs.filter(pick_checkpoint=checkpoint).count()
                    checkpoint.num_drops = this_race_jobs.filter(drop_checkpoint=checkpoint).count()
                
                import pdb
                #pdb.set_trace()
                cps = list(checkpoints)
                cps.sort(key=lambda x:-x.num_picks)
                most_picked_checkpoint = cps[0]
                cps.sort(key=lambda x:x.num_picks)
                least_picked_checkpoint = cps[0]
                cps.sort(key=lambda x:-x.num_drops)
                most_dropped_checkpoint = cps[0]
                cps.sort(key=lambda x:x.num_drops)
                least_dropped_checkpoint = cps[0]
                
                pick_diff = most_picked_checkpoint.num_picks - least_picked_checkpoint.num_picks
                drop_diff = most_dropped_checkpoint.num_drops - least_dropped_checkpoint.num_drops
                
                flagged = True
                
                while flagged:
                    
                    if pick_diff > 3:
                        pick_checkpoint = least_picked_checkpoint
                    else:
                        pick_checkpoint = random.choice(checkpoints)
                    if drop_diff > 3 and least_dropped_checkpoint!= pick_checkpoint:
                        drop_checkpoint = least_dropped_checkpoint
                    else:
                        drop_checkpoint = random.choice(checkpoints)
                    
                    if pick_checkpoint == drop_checkpoint:
                        flagged = True
                    if pick_checkpoint == most_picked_checkpoint or drop_checkpoint == most_dropped_checkpoint:
                        flagged = True
                    elif Job.objects.filter(pick_checkpoint=pick_checkpoint).filter(drop_checkpoint=drop_checkpoint).exists():
                        flagged = True
                    else:
                        flagged = False

                job = Job(job_id=job_id, race=race, pick_checkpoint=pick_checkpoint, drop_checkpoint=drop_checkpoint, minutes_ready_after_start=minutes_counter)
                job.manifest = manifest
                job.save()
                print job
                this_set_counter += 1
                job_counter += 1
                job_id += 1
            
       
        print "{} jobs created.".format(job_counter)