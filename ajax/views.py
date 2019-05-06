from django.shortcuts import render
from django.http import HttpResponseForbidden
from ajax.serializers import RacerSerializer, RaceEntrySerializer, JobSerializer, RunSerializer, RaceEntrySerializer, CompanyEntrySerializer
from racers.models import Racer
from raceentries.models import RaceEntry
from company_entries.models import CompanyEntry
from rest_framework import generics
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from jobs.models import Job
from runs.models import Run, RunChangeLog
from races.models import Race
from racecontrol.models import RaceControl
from streamer.models import StreamEvent
import datetime
import time
import requests
import json
import pytz
import decimal
from django.utils.timezone import utc
from racelogs.models import RaceLog
from django.db.models import Q, Sum

class JobAjaxView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = 'job_id'

class RacerAjaxView(generics.RetrieveAPIView):
    queryset = Racer.objects.all()
    serializer_class = RacerSerializer
    lookup_field = 'racer_number'

class RaceEntryAjaxView(APIView):
    def get(self, request):
        race_entry = RaceEntry.objects.filter(race=request.GET['race']).filter(racer__racer_number=request.GET['racer'])

        if len(race_entry) == 0:
            return Response({'detail' : 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serialized_entry = RaceEntrySerializer(race_entry[0])
        return Response(serialized_entry.data)

class StartRacerAjaxView(APIView):
    def post(self, request):
        racer_number = self.request.DATA['racer']
        race_id = self.request.DATA['race']
        race_entry = RaceEntry.objects.filter(race__pk=race_id).filter(racer__racer_number=racer_number).first()
        if not race_entry:
            return Response({'detail' : 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        if self.request.DATA.get('unstart'):
            race_entry.unstart_racer()
            RaceLog(racer=race_entry.racer, race=race_entry.race, user=request.user, log="Racer un-started in race.", current_grand_total=race_entry.grand_total, current_number_of_runs=race_entry.number_of_runs_completed).save()

            return Response({'error_description' : "Racer un-started"}, status=status.HTTP_200_OK)


        if race_entry.start_racer():
            tz = pytz.timezone('US/Eastern')
            time_due_back_string = race_entry.time_due_back(tz).strftime('%I:%M %p')

            RaceLog(racer=race_entry.racer, race=race_entry.race, user=request.user, log="Racer started in race.", current_grand_total=race_entry.grand_total, current_number_of_runs=race_entry.number_of_runs_completed).save()

            if race_entry.race.dispatch_race:
                runs = Run.objects.filter(race_entry=race_entry)
                runs_to_assign = runs.filter(utc_time_ready__lte=race_entry.start_time)
                from dispatch.util import assign_runs
                from dispatch.serializers import MessageSerializer
                message = assign_runs(runs_to_assign, race_entry)
                return Response({'message': MessageSerializer(message).data, 'error_description' : None, 'due_back' : time_due_back_string}, status=status.HTTP_200_OK)

            return Response({'due_back' : time_due_back_string})
        return Response(status=status.HTTP_400_BAD_REQUEST)

class FinishRacerAjaxView(APIView):
    def post(self, request):
        racer_number = self.request.DATA.get('racer')
        race_id = self.request.DATA.get('race')
        race_entry = RaceEntry.objects.filter(race__pk=race_id).filter(racer__racer_number=racer_number).first()
        if not race_entry:
            return Response({'detail' : 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if race_entry.finish_racer():
            race_entry.save()
            RaceLog(racer=race_entry.racer, race=race_entry.race, user=request.user, log="Racer finished race.", current_grand_total=race_entry.grand_total, current_number_of_runs=race_entry.number_of_runs_completed).save()
            return Response({
                'final_time' : race_entry.final_time_formatted
            })
        return Response(status=status.HTTP_400_BAD_REQUEST)

class MarkAsPaidRacerAjaxView(APIView):
    def post(self, request):
        print self.request.DATA
        racer_pk = self.request.DATA['racer_pk']
        try:
            racer = Racer.objects.get(pk=racer_pk)
            racer.mark_as_paid()
            return Response(status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DQRacerAjaxView(APIView):
    def post(self, request):
        racer_number = self.request.DATA['racer']
        race_id = self.request.DATA['race']
        dq_reason = self.request.DATA['dq_reason']
        race_entry = RaceEntry.objects.filter(race__pk=race_id).filter(racer__racer_number=racer_number)
        if len(race_entry) == 0:
            return Response({'detail' : 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if race_entry[0].dq_racer():
            race_entry[0].dq_reason = dq_reason
            race_entry[0].save()
            return Response()
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UnDQRacerAjaxView(APIView):
    def post(self, request):
        racer_number = self.request.DATA['racer']
        race_id = self.request.DATA['race']
        race_entry = RaceEntry.objects.filter(race__pk=race_id).filter(racer__racer_number=racer_number)
        if len(race_entry) == 0:
            return Response({'detail' : 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if race_entry[0].un_dq_racer():
            race_entry[0].save()
            return Response()
        return Response(status=status.HTTP_400_BAD_REQUEST)

class DNFRacerAjaxView(APIView):
    def post(self, request):
        racer_number = self.request.DATA['racer']
        race_id = self.request.DATA['race']
        race_entry = RaceEntry.objects.filter(race__pk=race_id).filter(racer__racer_number=racer_number)
        if len(race_entry) == 0:
            return Response({'detail' : 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if race_entry[0].dnf_racer():
            race_entry[0].save()
            return Response()
        return Response(status=status.HTTP_400_BAD_REQUEST)

class CheckJobAjaxView(APIView):
    def post(self, request):
        racer_number = self.request.DATA['racer']
        race_id = self.request.DATA['race']
        job_id = self.request.DATA['job']
        check_for_run = Run.objects.filter(race_entry__racer__racer_number=racer_number).filter(job__job_id=job_id).count()
        if check_for_run == 0:
            job = Job.objects.filter(job_id=job_id).filter(race__pk=race_id)
            if len(job) == 0:
                return Response({'detail' : 'Cannot locate job with that job number.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                job = job[0]
            serialized_job = JobSerializer(job)
            return Response(serialized_job.data, status=status.HTTP_200_OK)

        return Response({'detail' : 'Racer has already done job'}, status=status.HTTP_400_BAD_REQUEST)

class UpdateRacerNotes(APIView):
    def post(self, request):
        racer_number = self.request.DATA['racer']
        race_id = self.request.DATA['race']
        racer_notes = self.request.DATA['notes']
        race_entry = RaceEntry.objects.filter(race__pk=race_id).filter(racer__racer_number=racer_number)
        race_entry = race_entry[0]
        race_entry.scratch_pad = racer_notes
        race_entry.save()
        return Response()


class RunAjaxView(APIView):
    def post(self, request):
        racer_number = self.request.DATA['racer']
        race_id = self.request.DATA['race']
        job_id = self.request.DATA['job']

        try:
             job = Job.objects.get(job_id=job_id)
        except:
            return Response({'detail' : 'Job #{} not found'.format(str(job_id))}, status=status.HTTP_400_BAD_REQUEST)

        check_for_run = Run.objects.filter(race_entry__racer__racer_number=racer_number).filter(job=job).count()

        if check_for_run == 0:
            race_entry = RaceEntry.objects.filter(race__pk=race_id).filter(racer__racer_number=racer_number)
            race_entry = race_entry[0]
            run = Run()
            run.job = job
            run.points_awarded = job.points
            run.race_entry = race_entry
            run.save()
            race_entry.add_up_points()
            race_entry.add_up_runs()
            race_entry.save()
            return Response()
        return Response({'detail' : 'Racer has already done job'}, status=status.HTTP_400_BAD_REQUEST)

class AwardRacerAjaxView(APIView):
    def post(self, request):
        racer = request.DATA['racer']
        race = request.DATA['race']
        award = request.DATA['award']
        race_entry = RaceEntry.objects.filter(race__pk=race).filter(racer__racer_number=racer).first()
        race_entry.supplementary_points = decimal.Decimal(award)
        race_entry.add_up_points()
        race_entry.save()
        return Response()

class DeductRacerAjaxView(APIView):
    def post(self, request):
        racer = request.DATA['racer']
        race = request.DATA['race']
        award = request.DATA['deduction']
        race_entry = RaceEntry.objects.filter(race__pk=race).filter(racer__racer_number=racer).first()
        race_entry.deductions = decimal.Decimal(award)
        race_entry.add_up_points()
        race_entry.save()
        return Response()

class DeleteRunAjaxView(APIView):
    def post(self, request):
        try:
            run = Run.objects.get(pk=request.DATA['run'])
            race_entry = run.race_entry
            run.delete()
            race_entry.add_up_points()
            race_entry.add_up_runs()
            race_entry.save()
        except:
            pass
        return Response()

class SetRaceStartTime(APIView):
    def post(self, request):
        race = Race.objects.get(pk=request.DATA['race'])
        date_string = request.DATA['start_time']
        start_time = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        eastern = pytz.timezone('US/Eastern')
        localized_start_time = eastern.localize(start_time)
        race.race_start_time = localized_start_time
        race.save()
        return Response()

class SetCurrentRace(APIView):
    def post(self, request, *args, **kwargs):
        race = Race.objects.get(pk=request.DATA['race'])
        rc = RaceControl.shared_instance()
        rc.current_race = race
        rc.save()
        return Response()

class MassStartCompanies(APIView):
    def post(self, request, *args, **kwargs):
        rc = RaceControl.shared_instance()
        current_race = rc.current_race
        company_entries = CompanyEntry.objects.filter(race=current_race)

        if not rc.racers_started:
            for company_entry in company_entries:
                company_entry.start_racers()
            rc.racers_started = True
        else:
            pass
            #for company_entry in company_entries:
            #    if company_entry.entry_status == CompanyEntry.ENTRY_STATUS_RACING:
            #        company_entry.finish()
            #rc.racers_started = False
        rc.save()
        return Response()

class MassStartRacers(APIView):
    def post(self, request, *args, **kwargs):
        rc = RaceControl.shared_instance()
        if not rc.racers_started:
            race_entries = RaceEntry.objects.filter(race=rc.current_race)
            start_time = datetime.datetime.utcnow().replace(tzinfo=utc)
            for race_entry in race_entries:
                race_entry.entry_status = RaceEntry.ENTRY_STATUS_RACING
                race_entry.start_time = start_time
                race_entry.save()
            rc.racers_started = True
        else:
            race_entries = RaceEntry.objects.filter(race=rc.current_race)
            finish_time = datetime.datetime.utcnow().replace(tzinfo=utc)
            for race_entry in race_entries:
                if race_entry.entry_status == RaceEntry.ENTRY_STATUS_RACING:
                    race_entry.entry_status = RaceEntry.ENTRY_STATUS_FINISHED
                    race_entry.end_time = finish_time
                    race_entry.save()
            rc.racers_started = False
        rc.save()
        return Response()

class PostResultsStreamAjaxView(APIView):
    def post(self, request):
        race_id = self.request.DATA['race']
        endpoint = self.request.DATA['endpoint']

        #Get all the unposted stream events and serialize them
        events = StreamEvent.objects.filter(race__pk=race_id).filter(published=False)
        serialized_events = []
        for event in events:
            event_dict = {
                'timestamp'            : time.mktime(event.timestamp.timetuple()),
                'racer_number'         : str(event.racer.racer_number),
                'racer_name'           : event.racer.display_name,
                'city'                 : event.racer.city,
                'team'                 : event.racer.team,
                'message'              : event.message,
                'poster_name'          : event.poster_name,
                'poster_photo'         : event.poster_photo
            }
            serialized_events.append(event_dict)

        #Serialize the results
        standings = RaceEntry.objects.filter(race__pk=race_id).filter(
            ~Q(entry_status=RaceEntry.ENTRY_STATUS_ENTERED) |
            ~Q(entry_status=RaceEntry.ENTRY_STATUS_DQD) |
            ~Q(entry_status=RaceEntry.ENTRY_STATUS_CUT) |
            ~Q(entry_status=RaceEntry.ENTRY_STATUS_DNF))
        standings = standings.order_by('grand_total')
        serialized_standings = []
        counter = 1
        for standing in standings:
            standing_dict = {
                'place' : counter,
                'racer_number'         : str(standing.racer.racer_number),
                'racer_name'           : standing.racer.display_name,
                'city'                 : standing.racer.city,
                'team'                 : standing.racer.team,
                'current_earnings'     : float(standing.grand_total),
                "number_of_jobs"       : standing.number_of_jobs_completed
            }
            serialized_standings.append(standing_dict)
            counter += 1

        combined_results = {
            'events' : serialized_events,
            'standings' : serialized_standings
        }

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(endpoint, data=json.dumps(combined_results), headers=headers)

        events.update(published=True)

        return Response(combined_results)

class DispatchRefreshView(generics.ListAPIView):
    serializer_class = RunSerializer
    queryset = Run.objects.all()
    allowed_methods = [u'GET', u'HEAD', u'OPTIONS', u'POST']

    def post(self, request, *args, **kwargs):
        qs = self.queryset
        company_entry = CompanyEntry.objects.filter(company__dispatcher=self.request.user).first()

        if company_entry:
            qs = qs.filter(company_entry=company_entry)

            head_id = self.request.DATA.get('head', 0)
            if head_id:
                changes = RunChangeLog.objects.filter(company_pk=company_entry.pk).filter(id__gt=head_id).order_by('pk')

                if changes:
                    head_id = changes.last().pk

                changes_pks = changes.values_list('run_pk', flat=True)
                qs = qs.filter(pk__in=changes_pks)

        serialized_runs = RunSerializer(qs)
        return Response({'runs' : serialized_runs.data, 'head' : head_id}, status=status.HTTP_200_OK)

class DispatchAssignView(APIView):
    def post(self, request, *args, **kwargs):
        rc = RaceControl.shared_instance()
        if not rc.racers_started:
            return Response({'error_description' : "Race has not started yet!"}, status=status.HTTP_200_OK)

        current_race = rc.current_race

        time_now = datetime.datetime.now(tz=pytz.utc)

        company_entry = CompanyEntry.objects.filter(company__dispatcher=request.user).filter(race=current_race).first()
        if not company_entry:
            return HttpResponseForbidden

        if not company_entry.race == rc.current_race:
            return HttpResponseForbidden

        if current_race.race_end_time and time_now >= current_race.race_end_time:
            return Response({'error': True, 'error_title': "Race is over!", "error_description": "The race has ended. No further actions will be allowed."}, status=status.HTTP_200_OK)

        race_entry = RaceEntry.objects.get(pk=request.DATA.get('race_entry_pk'))

        if not race_entry.racer.company == company_entry.company:
            return HttpResponseForbidden

        allowed_race_entry_statuses = [RaceEntry.ENTRY_STATUS_RACING, RaceEntry.ENTRY_STATUS_ENTERED]
        if not race_entry.entry_status in allowed_race_entry_statuses:
            return Response({'error_description' : "Racer status invalid: Racer must be Racing or assigned."}, status=status.HTTP_200_OK)


        run = Run.objects.get(pk=request.DATA.get('run_pk'))
        allowed_run_statuses = [Run.RUN_STATUS_PENDING, Run.RUN_STATUS_ASSIGNED]
        if not run.status in allowed_run_statuses:
            return Response({'error_description' : "Job status invalid: Job must be pending or assigned."}, status=status.HTTP_200_OK)


        run.status = Run.RUN_STATUS_ASSIGNED
        run.determination = Run.DETERMINATION_NOT_PICKED
        run.utc_time_assigned = time_now
        run.race_entry = race_entry
        run.save()
        run = RunSerializer(run)
        #TODO log
        #RaceLog(racer=race_entry.racer, race=race_entry.race, user=request.user, log="Racer un-started in race.", current_grand_total=race_entry.grand_total, current_number_of_runs=race_entry.number_of_runs_completed).save()

        return Response(run.data, status=status.HTTP_200_OK)

class DispatchUnassignView(APIView):
    def post(self, request, *args, **kwargs):
        rc = RaceControl.shared_instance()
        if not rc.racers_started:
            return Response({'error_description' : "Race has not started yet!"}, status=status.HTTP_200_OK)

        current_race = rc.current_race

        time_now = datetime.datetime.now(tz=pytz.utc)

        company_entry = CompanyEntry.objects.filter(company__dispatcher=request.user).filter(race=current_race).first()
        if not company_entry:
            return HttpResponseForbidden

        if not company_entry.race == rc.current_race:
            return HttpResponseForbidden

        if current_race.race_end_time and time_now >= current_race.race_end_time:
            return Response({'error': True, 'error_title': "Race is over!", "error_description": "The race has ended. No further actions will be allowed."}, status=status.HTTP_200_OK)


        run = Run.objects.get(pk=request.DATA.get('run_pk'))
        allowed_run_statuses = [Run.RUN_STATUS_ASSIGNED]
        if not run.status in allowed_run_statuses:
            return Response({'error_description' : "Job status invalid: This job cannot be unassigned."}, status=status.HTTP_200_OK)


        run.status = Run.RUN_STATUS_PENDING
        run.determination = Run.DETERMINATION_NOT_PICKED
        run.utc_time_assigned = None
        run.race_entry = None
        run.save()
        run = RunSerializer(run)

        return Response(run.data, status=status.HTTP_200_OK)


class DispatchScoreboardRefreshView(APIView):
    allowed_methods = [u'GET']

    def post(self, request, *args, **kwargs):
        rc = RaceControl.shared_instance()
        current_race = rc.current_race

        company_entries = CompanyEntry.objects.filter(race=current_race)
        serializer = CompanyEntrySerializer
        serialized_company_entries = CompanyEntrySerializer(company_entries)

        runs = Run.objects.filter(company_entry__in=company_entries)

        head_id = self.request.DATA.get('head', 0)
        if head_id:
            changes = RunChangeLog.objects.filter(id__gt=head_id).order_by('pk')

            if changes:
                head_id = changes.last().pk

            changes_pks = changes.values_list('run_pk', flat=True)
            runs = runs.filter(pk__in=changes_pks)

        serialized_runs = RunSerializer(runs)

        return Response({'runs' : serialized_runs.data, 'company_entries' : serialized_company_entries.data, 'head' : head_id}, status=status.HTTP_200_OK)
