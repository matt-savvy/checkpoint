from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from nacccusers.auth import AuthorizedRaceOfficalMixin
from races.models import Race
from raceentries.models import RaceEntry
from runs.models import Run
import pytz
import datetime

class CommissionView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "commission.html"
    
    def get_context_data(self, **kwargs):
        context = {}
        context['race'] = Race.objects.get(pk=kwargs['race'])
        context['racer'] = RaceEntry.objects.filter(race=context['race']).filter(racer__racer_number=kwargs['racer']).first()
        eastern = pytz.timezone('US/Eastern')
        runs = Run.objects.filter(race_entry=context['racer'])
        context['runs'] = []
        for run in runs:
            run_dict = {}
            run_dict['job_number'] = run.job.job_id
            run_dict['run_id'] = run.pk
            run_dict['pick'] = run.job.pick_checkpoint
            run_dict['drop'] = run.job.drop_checkpoint
            
            run_dict['time_picked']= run.utc_time_picked.astimezone(eastern).strftime('%I:%M %p')
            if run.utc_time_dropped:
                run_dict['time_dropped'] = run.utc_time_dropped.astimezone(eastern).strftime('%I:%M %p')
            else:
                run_dict['time_dropped'] = 'n/a'
            
            due_time = context['race'].race_start_time.astimezone(pytz.utc) + datetime.timedelta(minutes=run.job.minutes_due_after_start)
            due_time = due_time.astimezone(eastern)
            run_dict['due_time']= due_time.strftime('%I:%M %p')
            run_dict['determination'] = run.determination_as_string
            run_dict['payout'] = run.points_awarded
            context['runs'].append(run_dict)
        return context

class RunListView(ListView):
    model = Run
    context_object_name = 'runs'
    
    def get_queryset(self):
        return Run.objects.filter(race_entry__race__pk=self.kwargs['race'])
    
