from django.shortcuts import render
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import CheckpointSerializer, RacerSerializer
from ajax.serializers import JobSerializer, RunSerializer, RaceEntrySerializer
from checkpoints.models import Checkpoint
from racers.models import Racer
from races.models import Race
from racecontrol.models import RaceControl
from raceentries.models import RaceEntry
from jobs.models import Job
from runs.models import Run
from racelogs.models import RaceLog
from mobilecheckpoint.util import get_available_runs
import datetime
import pytz

class AvailableCheckpointsView(APIView):
    
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        checkpoints = request.user.authorized_checkpoints.all()
        serialized_checkpoints = CheckpointSerializer(checkpoints)
        return Response(serialized_checkpoints.data, status=status.HTTP_200_OK)
        

class PingView(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        current_race = RaceControl.shared_instance().current_race
        context = {
            'successful' : True,
            'current_race' : current_race.race_name,
            'race_start_time' : current_race.race_start_time
        }
        return Response(context, status=status.HTTP_200_OK)

class CheckpointIdentificationView(APIView):
    def post(self, request, *args, **kwargs):
        checkpoint_number = request.DATA['checkpoint']
        try:
            checkpoint = Checkpoint.objects.get(checkpoint_number=checkpoint_number)
            context = {
                'checkpoint_number' : checkpoint.checkpoint_number,
                'checkpoint_name' : checkpoint.checkpoint_name,
                'request_user' : request.user.username
            }
            return Response(context, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RacerDetailView(generics.RetrieveAPIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    serializer_class = RacerSerializer
    model = Racer
    lookup_field = 'racer_number'

class RacerCheckpointView(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        current_race = RaceControl.shared_instance().current_race
        right_now = datetime.datetime.now(tz=pytz.utc)
        racer_number = request.DATA.get('racer_number')
        racer = Racer.objects.filter(racer_number=racer_number).first()
        
        checkpoint = request.DATA['checkpoint']
        
        if racer:
            race_entry = RaceEntry.objects.filter(racer=racer).filter(race=current_race).first()
            if race_entry:
                if race_entry.entry_status == RaceEntry.ENTRY_STATUS_FINISHED or race_entry.entry_status == RaceEntry.ENTRY_STATUS_PROCESSING:
                    return Response({'error': True, 'error_title': "Racer is finished!", "error_description": "This racer has already finished the race"}, status=status.HTTP_200_OK)
                
                elif race_entry.entry_status == RaceEntry.ENTRY_STATUS_DQD:
                    return Response({'error': True, 'error_title': "Racer has been disqualified!", "error_description": "This racer is marked as disqualified. Have them report to headquarters."}, status=status.HTTP_200_OK)
                
                elif race_entry.entry_status == RaceEntry.ENTRY_STATUS_ENTERED:
                    return Response({'error': True, 'error_title': "Racer has not started!", "error_description": "This racer has not started their race yet."}, status=status.HTTP_200_OK)
                
                if race_entry.race_end_time:
                    if right_now >= race_entry.race_end_time:
                        return Response({'error': True, 'error_title': "Race is over!", "error_description": "The race has ended. No further actions will be allowed."}, status=status.HTTP_200_OK)
                
                if race_entry.entry_status == RaceEntry.ENTRY_STATUS_RACING or race_entry.entry_status == RaceEntry.ENTRY_STATUS_CUT:
                    available_runs = get_available_runs(race_entry, checkpoint)
                    serialized_runs = RunSerializer(available_runs)
                    serialized_racer = RacerSerializer(racer)
                                
                    return Response({'racer' : serialized_racer.data, 'runs' : serialized_runs.data, 'error' : False, 'error_title' : None, 'error_description' : None}, status=status.HTTP_200_OK)
            else:
                return Response({'error' : True, 'error_title' : 'Cannot Find Racer', 'error_description' : 'Please refresh your browser.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error' : True, 'error_title' : 'Cannot Find Racer', 'error_description' : 'No racer found with racer number {}.'.format(str(racer_number))}, status=status.HTTP_200_OK)

class PickView(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):     
        current_race = RaceControl.shared_instance().current_race
        racer_number = request.DATA.get('racer_number')
        run_number = request.DATA.get('run')
        checkpoint = request.DATA.get('checkpoint')
        
        race_id = request.DATA.get('race')
        
        try:
            race = Race.objects.get(pk=race_id)
            if  current_race != race:
                return Response({'error' : True, 'error_title' : 'Current Race Changed', 'error_description' : 'Please reload your browser to update race info.'}, status=status.HTTP_200_OK)
        except:
            return Response({'error' : True, 'error_title' : 'Race Not Found', 'error_description' : 'Please reload your browser to update race info.'}, status=status.HTTP_200_OK)
        

        #pdb.set_trace()
        run = Run.objects.filter(pk=run_number).filter(race_entry__racer__racer_number=racer_number).filter()
        
        #Check for run
        if not run.exists():
            return Response({'confirm_code' : None, 'error' : True, 'error_title' : 'Cannot Find Job', 'error_description' : 'No job found.'}, status=status.HTTP_200_OK)
        
        #run is valid
        run = run.first()
        
        #Check to make sure racer is at right checkpoint
        if run.job.pick_checkpoint.pk != checkpoint:
            return Response({'confirm_code' : None, 'error' : True, 'error_title' : 'Wrong Checkpoint', 'error_description' : 'This pick up needs to be made at {}.'.format(str(run.job.pick_checkpoint.checkpoint_name))}, status=status.HTTP_200_OK)
                
        #Make sure the racer is entered in the race
        race_entry = RaceEntry.objects.filter(race=current_race).filter(racer__racer_number=racer_number)
        
        if not race_entry.exists():
            return Response({'confirm_code' : None, 'error' : True, 'error_title' : 'Racer not entered in race.', 'error_description' : 'No racer found with racer number {} is entered in this race.'.format(str(racer_number))}, status=status.HTTP_200_OK)
        
        #Racer is in race, grab her/his race entry
        race_entry = race_entry.first()
        
        #Check to make sure Racer is not DQ'd
        if race_entry.entry_status == RaceEntry.ENTRY_STATUS_DQD:
            return Response({'confirm_code' : None, 'error' : True, 'error_title' : 'Racer has been Disqualified', 'error_description' : '#{} has been disqualified from the race. Have the racer report to HQ if they have any questions.'.format(str(racer_number))}, status=status.HTTP_200_OK)
        
        #Check if Racer has already picked or dropped this run
        
        if run.status == Run.RUN_STATUS_PICKED:
            pick_time_localized = localize_time(run.utc_time_picked)
            return Response({'confirm_code' : None, 'error' : True, 'error_title' : 'Racer already picked up job.', 'error_description' : 'The racer has already picked job {}, the confirm code was {} at {}'.format(str(run.job), str(run.pk), pick_time_localized)}, status=status.HTTP_200_OK)
        elif run.status == Run.RUN_STATUS_COMPLETED:
            drop_time_localized = localize_time(run.utc_time_dropped)
            return Response({'confirm_code' : None, 'error' : True, 'error_title' : 'Racer already delivered job.', 'error_description' : 'The racer has already done job {}, the confirm code was {}'.format(str(run.job), drop_time_localized)}, status=status.HTTP_200_OK)
        
        #check if job is ready
        if datetime.datetime.now(tz=pytz.utc) <= run.utc_time_ready:            
            ready_time_localized = localize_time(run.utc_time_ready)
            return Response({'confirm_code' : None, 'error' : True, 'error_title' : 'Job is not ready yet.', 'error_description' : 'Job is not ready until {}.'.format(ready_time_localized)}, status=status.HTTP_200_OK)
        
        #Check to see if job is still alive
        #
        #due_time = current_race.race_start_time.astimezone(pytz.utc) + datetime.timedelta(minutes=run.job.minutes_due_after_start)
        #if datetime.datetime.now(tz=pytz.utc) > due_time:
        #    due_time_localized = localize_time(due_time)
        #    return Response({'confirm_code' : None, 'error' : True, 'error_title' : 'Job is Dead.', 'error_description' : 'Job died at {}.'.format(due_time_localized)}, status=status.HTTP_200_OK)
        
        #All checks have passed, lets create the run
        run.pick()
        
        try:
            RaceLog(racer=race_entry.racer, race=race_entry.race, user=request.user, log="Racer picked up run #{}".format(str(run.pk)), current_grand_total=race_entry.grand_total, current_number_of_runs=race_entry.number_of_runs_completed).save()
        except:
            pass
        
        return Response({'confirm_code' : run.pk, 'error' : False, 'error_title' : None, 'error_description' : None}, status=status.HTTP_200_OK)

def localize_time(utc_time):
    eastern = pytz.timezone('US/Eastern')
    return utc_time.astimezone(eastern).strftime('%I:%M %p')

class DropView(APIView):
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        current_race = RaceControl.shared_instance().current_race
        race_id = request.DATA.get('race')
        
        try:
            race = Race.objects.get(pk=race_id)
            if  current_race != race:
                return Response({'error' : True, 'error_title' : 'Current Race Changed', 'error_description' : 'Please reload your browser to update race info.'}, status=status.HTTP_200_OK)
        except:
            return Response({'error' : True, 'error_title' : 'Race Not Found', 'error_description' : 'Please reload your browser to update race info.'}, status=status.HTTP_200_OK)
             
        
        racer_number = request.DATA.get('racer_number')
        confirm_code = request.DATA.get('confirm_code')
        checkpoint = request.DATA.get('checkpoint')
        
        try:
            run = Run.objects.get(pk=confirm_code)
        except:
            return Response({'error' : True, 'error_title' : 'Cannot Find Confirm Code', 'error_description' : "No jobs' assoicated with confirm code {}.".format(str(confirm_code))}, status=status.HTTP_200_OK)
            
        #Make sure racer is authorized to make drop
        if run.race_entry.racer.racer_number != racer_number:
            return Response({'error' : True, 'error_title' : 'Wrong Racer #', 'error_description' : 'Racer # {} does not a drop off with confirm code {}.'.format(str(racer_number), str(confirm_code))}, status=status.HTTP_200_OK)

        #Check to make sure racer is at right checkpoint
        if run.job.drop_checkpoint.pk != checkpoint:
            return Response({'error' : True, 'error_title' : 'Wrong Checkpoint', 'error_description' : 'This drop off needs to be made at {}.'.format(str(run.job.drop_checkpoint.checkpoint_name))}, status=status.HTTP_200_OK)
                
        #Check to make sure Racer hasn't already dropped off job
        if run.status == Run.RUN_STATUS_COMPLETED:
            eastern = pytz.timezone('US/Eastern')
            drop_time_localized = run.utc_time_dropped.astimezone(eastern).strftime('%I:%M %p')
            return Response({'error' : True, 'error_title' : 'Job already dropped off', 'error_description' : 'The run was already dropped off at {}.'.format(str(drop_time_localized))}, status=status.HTTP_200_OK)
        
        run.drop()
        
        run.race_entry.add_up_points()
        run.race_entry.add_up_runs()
        run.race_entry.save()
        
        try:
            RaceLog(racer=run.race_entry.racer, race=run.race_entry.race, user=request.user, log="Racer dropped off job #{}".format(str(run.job.job_id)), current_grand_total=run.race_entry.grand_total, current_number_of_runs=run.race_entry.number_of_runs_completed).save()
        except:
            pass
        
        return Response({'error' : False, 'error_title' : None, 'error_description' : None}, status=status.HTTP_200_OK)