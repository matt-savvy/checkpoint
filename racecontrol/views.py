from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from django.views.generic.list import ListView
from django.views.generic import View, TemplateView

from races.models import Race
from raceentries.models import RaceEntry
from runs.models import Run
from .models import RaceControl
from nacccusers.auth import AuthorizedRaceOfficalMixin

import datetime
import pytz

class RaceControlRaceListView(AuthorizedRaceOfficalMixin, ListView):
    model = Race
    template_name = "racecontrol_race_select.html"
    context_object_name = 'races'
    
    def get_queryset(self):
        return Race.objects.all()
        
class RaceControlView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "race_control.html"
    
    def get_context_data(self, **kwargs):
        context = super(RaceControlView, self).get_context_data(**kwargs)
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        context['race'] = race
        return context
        
class NotRacedView(AuthorizedRaceOfficalMixin, ListView):
    model = Race
    template_name = "not_raced.html"
    context_object_name = 'raceentries'
    
    def get_queryset(self):
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        return RaceEntry.objects.filter(race=race).filter(entry_status=RaceEntry.ENTRY_STATUS_ENTERED).order_by('racer__racer_number')
    
    def get_context_data(self, **kwargs):
        context = super(NotRacedView, self).get_context_data(**kwargs)
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        context['total_racers'] = RaceEntry.objects.filter(race=race).count()
        return context

class CurrentRacingView(AuthorizedRaceOfficalMixin, ListView):
    model = RaceEntry
    template_name = "racing.html"
    context_object_name = 'raceentries'
    
    def get_queryset(self):
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        return RaceEntry.objects.filter(race=race).filter(entry_status=RaceEntry.ENTRY_STATUS_RACING).order_by('racer__racer_number')

class RacerInfoView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "racer_info.html"

class RacerDetailAjaxView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = 'racer_ajax_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super(RacerDetailAjaxView, self).get_context_data(**kwargs)
        race_entry = RaceEntry.objects.filter(racer__racer_number=self.request.GET['racer']).filter(race__pk=self.request.GET['race'])
        if len(race_entry) == 1:
            context['found_racer'] = True
            context['race_entry'] = race_entry[0]
            runs = Run.objects.filter(race_entry__race__pk=self.request.GET['race']).filter(race_entry__racer__racer_number=self.request.GET['racer'])
            context['runs'] = runs
            eastern_tz = pytz.timezone('US/Eastern')
            
            if race_entry[0].start_time:
                start_time = race_entry[0].start_time.astimezone(eastern_tz)
                context['start_time'] = datetime.datetime.strftime(start_time, '%I:%M %p')
                context['due_back_time'] = datetime.datetime.strftime(race_entry[0].time_due_back(eastern_tz), '%I:%M %p')
            
            if race_entry[0].entry_status == RaceEntry.ENTRY_STATUS_RACING:
                context['time_status'] = 'Current Elasped Time'
            else:
                context['time_status'] = 'Final Time'
            
        else:
            context['found_racer'] = False
        return context

class StartView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "start_racer.html"

class FinishView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "finish_racer.html"

class DQView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "dq_racer.html"

class DNFView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "dnf_racer.html"
    
class RunEntryView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = 'run_entry.html'

class AwardView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = 'award_racer.html'

class DeductView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = 'deduct_racer.html'

class RaceStatusView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = 'race_status.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        current_race = RaceControl.shared_instance().current_race
        context['race'] = Race.objects.get(pk=kwargs['pk'])
        context['current_race'] = current_race
        
        eastern = pytz.timezone('US/Eastern')
        if current_race.race_start_time:
            context['start_time_set'] = True
            context['start_time_set'] = True
            race_start = current_race.race_start_time.astimezone(eastern)
            context['race_start_date'] = race_start.strftime('%Y-%m-%d')
            context['race_start_time'] = race_start.strftime('%H:%M')
        else:
            context['start_time_set'] = False
            race_start = datetime.datetime.now(tz=eastern).astimezone(eastern)
            context['race_start_date'] = race_start.strftime('%Y-%m-%d')
            context['race_start_time'] = race_start.strftime('%H:%M')
            context['start_time_set'] = False
        return context

class MassStartView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = 'mass_start.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        current_race = RaceControl.shared_instance()
        context['race'] = Race.objects.get(pk=kwargs['pk'])
        context['current_race'] = current_race
        return context        

class RacerRunEntryView(AuthorizedRaceOfficalMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            racer = RaceEntry.objects.filter(racer__racer_number=self.kwargs['racer']).filter(race__pk=self.kwargs['race']).first()
        except:
            return render(request, 'racer_run_entry_404.html', {'racer_number' : self.kwargs['racer']})
        
        context = {'race_entry' : racer}
        context['runs'] = Run.objects.filter(race_entry__race__pk=self.kwargs['race']).filter(race_entry__racer__racer_number=self.kwargs['racer']).order_by('job__job_id')
        return render(request, 'racer_run_entry.html', context)

class StandingsView(AuthorizedRaceOfficalMixin, ListView):
    model = RaceEntry
    template_name = "standings.html"
    context_object_name = 'raceentries'

    def get_queryset(self):
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        return RaceEntry.objects.filter(race=race).filter(Q(entry_status=RaceEntry.ENTRY_STATUS_RACING) | Q(entry_status=RaceEntry.ENTRY_STATUS_FINISHED) | Q(entry_status=RaceEntry.ENTRY_STATUS_CUT)| Q(entry_status=RaceEntry.ENTRY_STATUS_PROCESSING)).order_by('-grand_total')

