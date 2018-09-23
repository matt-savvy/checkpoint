from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic import View, TemplateView
from raceentries.models import RaceEntry
from raceentries.forms import AdvanceForm
from races.models import Race
from racers.models import Racer
from runs.models import Run
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from nacccusers.auth import AuthorizedRaceOfficalMixin
from racelogs.models import RaceLog
from racecontrol.models import RaceControl

class RaceEntryRaceListView(AuthorizedRaceOfficalMixin, ListView):
    model = Race
    template_name = "entries_race_select.html"
    context_object_name = 'races'
    
    def get_queryset(self):
        return Race.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(RaceEntryRaceListView, self).get_context_data(**kwargs)
        from django.db.models import Count
        
        #races = Race.objects.all()
        races = Race.objects.annotate(num_race_entries=Count('raceentry'))

        context['races'] = races
        # racers_in_race = RaceEntry.objects.all().filter()
#         RaceEntry_counts = []
#         for race in races_in_RaceEntrys:
#             count = RaceEntry.objects.filter(race=race.race).count()
#             RaceEntry_counts.append(count)
#         for x in range(0, len(context['RaceEntrys'])):
#             context['RaceEntrys'][x].RaceEntry_counts = RaceEntry_counts[x]
        return context

class ManageRaceEntryView(AuthorizedRaceOfficalMixin, TemplateView):
    
    template_name = 'manage_race_entries.html'
    
    def get_context_data(self, **kwargs):
        context = super(ManageRaceEntryView, self).get_context_data(**kwargs)
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        context['race'] = race
        
        race_entries = RaceEntry.objects.filter(race=race)
        context['race_entries'] = race_entries
        
        racers = Racer.objects.all()
        not_in_race = []
        
        #Seems rather un-pythonic. Must be a faster way?
        for racer in racers:
            found = False
            for entry in race_entries:
                if entry.racer == racer:
                    found = True
                    break 
            if not found:
                not_in_race.append(racer)
        context['not_in_race'] = not_in_race
        return context
        
class CutListView(AuthorizedRaceOfficalMixin, TemplateView):
    model = RaceEntry
    template_name = 'manage_eliminations.html'
    
    def last_stop(self, entry):
        last_pick = Run.objects.filter(race_entry=entry).filter(status=Run.RUN_STATUS_PICKED).order_by('utc_time_picked').last()
        last_drop = Run.objects.filter(race_entry=entry).filter(status=Run.RUN_STATUS_COMPLETED).order_by('utc_time_dropped').last()
        
        if last_pick and last_drop:
            last_pick_time = last_pick.utc_time_picked
            last_drop_time = last_drop.utc_time_dropped
        
            if last_drop_time >= last_pick_time:
                return last_drop_time
            elif last_pick_time > last_drop_time:
                return last_pick_time
        elif last_pick:
            return last_pick.utc_time_picked
        elif last_drop:
            return last_drop.utc_time_dropped
        
        return None
        
    def get_context_data(self, **kwargs):
        import pdb
        context = super(CutListView, self).get_context_data(**kwargs)
        current_race = RaceControl.shared_instance().current_race
        race_entries = list(RaceEntry.objects.filter(race=current_race))
        
        men_to_keep = self.request.GET.get('men_to_keep', 15)
        wtf_to_keep = self.request.GET.get('wtf_to_keep', 8)
        
        for entry in race_entries:
            entry.score = entry.calculate_current_score()
            entry.last_stop = self.last_stop(entry)
        race_entries.sort(key=lambda x: (-x.score, x.last_stop))

        men = [entry for entry in race_entries if entry.racer.gender==Racer.GENDER_MALE]
        wtf = [entry for entry in race_entries if entry.racer.gender!=Racer.GENDER_MALE]
        working_men = [entry for entry in men if entry.racer.category==Racer.RACER_CATEGORY_MESSENGER]
        working_wtf = [entry for entry in wtf if entry.racer.category==Racer.RACER_CATEGORY_MESSENGER]
        
        for racer in race_entries:
            if racer in working_men[:20] or racer in working_wtf[:5]:
                racer.cut = False
            elif racer in men[:men_to_keep] or racer in wtf[:wtf_to_keep]:
                racer.cut = False
            else:
                racer.cut = True
        
        ###TODO filter it also one level deeper on whatever criteria we are going to use to split ties of the same dollar amount.
        ###TODO maybe we just make a field on the db, and run a quick collection script that saves all the data and we can do some simple filters
        
        context['men'] = men
        context['wtf'] = wtf
        context['race'] = current_race
        from django.utils import timezone
        import pytz
        est = pytz.timezone('US/Eastern')
        timezone.activate(est)
        return context

class EnterRacersView(AuthorizedRaceOfficalMixin, View):
    def post(self, request, *args, **kwargs):
        race = Race.objects.get(pk=self.request.POST['race-id'])
        if 'enter-racers' in self.request.POST:
            racer_ids = self.request.POST.getlist('enter-in-race[]')
            if racer_ids:
                for racer_id in racer_ids:
                    try:
                        re = RaceEntry()
                        re.race = race
                        re.racer = Racer.objects.get(pk=int(racer_id))
                        re.save()
                        if race.race_type == Race.RACE_TYPE_DISPATCH_FINALS:
                            race.populate_runs(re)
                        RaceLog(racer=re.racer, race=race, user=request.user, log="Racer entered in race", current_grand_total=re.grand_total, current_number_of_runs=re.number_of_runs_completed).save()
                    except IntegrityError as ex:
                        pass         
        else:
            entry_ids = self.request.POST.getlist('remove-from-race[]')
            if entry_ids:
                for entry_id in entry_ids:
                    try:
                        re = RaceEntry.objects.get(pk=int(entry_id))
                        RaceLog(racer=re.racer, race=race, user=request.user, log="Racer was removed from race", current_grand_total=re.grand_total, current_number_of_runs=re.number_of_runs_completed).save()
                        re.delete()
                    except:
                        import sys
                        e = sys.exc_info()[0]
                        print e
        return redirect('/raceentries/race/' + str(race.id) + '/') 

class AdvanceView(AuthorizedRaceOfficalMixin, FormView):
    template_name = 'advance.html'
    form_class = AdvanceForm
    
    def get_context_data(self, **kwargs):
        context = super(AdvanceView, self).get_context_data(**kwargs)
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        context['race'] = race
        return context
    
    def form_valid(self, form):
        self.success_url = "/raceentries/race/" + str(form.cleaned_data['race_id'])
        return super(AdvanceView, self).form_valid(form)