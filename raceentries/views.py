from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic import View, TemplateView
from raceentries.models import RaceEntry
from raceentries.forms import AdvanceForm, CutForm
from races.models import Race, Manifest
from racers.models import Racer
from runs.models import Run
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from nacccusers.auth import AuthorizedRaceOfficalMixin
from racelogs.models import RaceLog
from racecontrol.models import RaceControl
from django.utils import timezone
import pytz
import pdb
        
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
        
        return entry.start_time
    
    def get_cut_racers(self):
        current_race = RaceControl.shared_instance().current_race
        race_entries = list(RaceEntry.objects.filter(race=current_race).filter(entry_status=RaceEntry.ENTRY_STATUS_RACING))

        men_to_keep = int(self.request.POST.get('men_to_keep', 30))
        wtf_to_keep = int(self.request.POST.get('wtf_to_keep', 10))
        messengers_only = self.request.POST.get('messengers_only', False)
        
        racers = {}
        racers['men'] = []
        racers['wtf'] = []
        
        for entry in race_entries:
            entry.score = entry.calculate_current_score()
            entry.last_stop = self.last_stop(entry)
            entry.cut = True
        race_entries.sort(key=lambda x: (-x.score, x.last_stop))
        
        working_men = [entry for entry in race_entries if entry.racer.category == Racer.RACER_CATEGORY_MESSENGER and entry.racer.gender == Racer.GENDER_MALE]
        working_wtf = [entry for entry in race_entries if entry.racer.category == Racer.RACER_CATEGORY_MESSENGER and entry.racer.gender != Racer.GENDER_MALE]
        
        
        if messengers_only:
            print "messengers only"
            
            working_men = working_men[:men_to_keep]
            working_wtf = working_wtf[:wtf_to_keep]
            print "len(working men) ", len(working_men)  
            print "len(working wtf) ", len(working_wtf)      
        else:
            working_men = working_men[:20]
            working_wtf = working_wtf[:5]
        
            men = [entry for entry in race_entries if entry.racer.gender==Racer.GENDER_MALE and not entry in working_men]
            wtf = [entry for entry in race_entries if entry.racer.gender!=Racer.GENDER_MALE and not entry in working_wtf]
            
            men_to_keep = men_to_keep - len(working_men)
            wtf_to_keep = wtf_to_keep - len(working_wtf)
            
            for racer in race_entries:
                if racer.cut:
                    if racer in men[:men_to_keep] or racer in wtf[:wtf_to_keep]:
                        racer.cut = False
            
        for entry in working_men:
            entry.cut = False
        for entry in working_wtf:
            entry.cut = False
                    
        for entry in race_entries:
            if entry.racer.gender == Racer.GENDER_MALE:
                racers['men'].append(entry)
            else:
                racers['wtf'].append(entry)
        return racers
    
    def get_context_data(self, **kwargs):
        context = super(CutListView, self).get_context_data(**kwargs)
        current_race = RaceControl.shared_instance().current_race

        racers = self.get_cut_racers()
        context['men'] = racers['men']
        context['wtf'] = racers['wtf']
        context['race'] = current_race
        context['form'] = CutForm(data={'wtf_to_keep':10, 'men_to_keep': 30})
        est = pytz.timezone('US/Eastern')
        timezone.activate(est)
        return context
    
    def post(self, request, *args, **kwargs):
        current_race = RaceControl.shared_instance().current_race
        
        import pdb
        #pdb.set_trace()
        
        if 'preview' in self.request.POST:
            context = self.get_context_data(**kwargs)
            context['form'] = CutForm(data=self.request.POST)
            context['preview'] = True
            return self.render_to_response(context)  
        
        racers_to_cut = self.request.POST.getlist('racers-to-cut[]')
        racers_to_cut = [int(x) for x in racers_to_cut]
        racers = list(RaceEntry.objects.filter(race=current_race).filter(entry_status=RaceEntry.ENTRY_STATUS_RACING))
        
        for entry in racers:
            entry.score = entry.calculate_current_score()
            entry.last_stop = self.last_stop(entry)
            if entry.pk in racers_to_cut:
                entry.entry_status = RaceEntry.ENTRY_STATUS_CUT
                entry.cut = True
                entry.save()
        
        messages.success(self.request, '{} Racers have been marked as cut.'.format(len(racers_to_cut)))
        
        context = {}
        context['men'] = [entry for entry in racers if entry.racer.gender==Racer.GENDER_MALE]
        context['wtf'] = [entry for entry in racers if entry.racer.gender!=Racer.GENDER_MALE]
        context['complete'] = True
        context['race'] = current_race
        return self.render_to_response(context) 

class EnterRacersView(AuthorizedRaceOfficalMixin, View):
    def post(self, request, *args, **kwargs):
        race = Race.objects.get(pk=self.request.POST['race-id'])
        manifests = list(Manifest.objects.filter(race=race).exclude(manifest_type=Manifest.TYPE_CHOICE_BONUS))
        manifest_count = len(manifests)
        
        if 'enter-racers' in self.request.POST:
            racer_ids = self.request.POST.getlist('enter-in-race[]')
            if racer_ids:
                for x, racer_id in enumerate(racer_ids):
                    try:
                        re = RaceEntry()
                        re.race = race
                        re.racer = Racer.objects.get(pk=int(racer_id))
                        if manifests:
                            re.manifest = manifests[x % manifest_count]
                            print re.manifest
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
        advance_to = get_object_or_404(Race, pk=self.kwargs['pk'])
        advance_from = form.cleaned_data['advance_from']
        racers = RaceEntry.objects.filter(race=advance_from).filter(entry_status=RaceEntry.ENTRY_STATUS_FINISHED)
        if form.cleaned_data['advance_using'] == form.ADVANCE_FROM_POINTS:
            for racer in racers:
                racer.last_drop = Run.objects.filter(status=Run.RUN_STATUS_COMPLETED).order_by('utc_time_dropped').last()
                racer.elapsed_time_til_last_drop = racer.last_drop.utc_time_dropped - racer.start_time
            racers = list(racers)
            racers.sort(key=lambda x: (-x.grand_total, x.elapsed_time_til_last_drop))
            
            men_racers = [entry for entry in racers if entry.racer.gender == Racer.GENDER_MALE]
            wtf_racers = [entry for entry in racers if entry.racer.gender != Racer.GENDER_MALE]
            men_advanced = 0
            wtf_advanced = 0
            try:
                starting_position = RaceEntry.objects.filter(race=advance_to).order_by('starting_position').first().starting_position
            except:
                starting_position = 1
            
            while men_racers or wtf_racers:
                if men_racers: 
                    racer = men_racers.pop(0)
                    if men_advanced <= form.cleaned_data['men_to_advance']:
                        re = RaceEntry(racer=racer.racer, race=advance_to, starting_position=starting_position)
                        re.save()
                        men_advanced += 1
                        starting_position += 1
                if wtf_racers:
                    racer = wtf_racers.pop(0)
                    if wtf_advanced <= form.cleaned_data['wtf_to_advance']:
                        re = RaceEntry(racer=racer.racer, race=advance_to, starting_position=starting_position)
                        re.save()
                        wtf_advanced += 1
                        starting_position += 1
                if men_advanced >= form.cleaned_data['men_to_advance'] and wtf_advanced >= form.cleaned_data['wtf_to_advance']:
                    break 
            if racers:
                messages.success(self.request, '{} Racers have been advanced to {}.'.format(starting_position, advance_to))
            else:
                messages.warning(self.request, 'No Racers have been advanced.')
        
        self.success_url = "/raceentries/race/" + str(form.cleaned_data['race_id'])
        return super(AdvanceView, self).form_valid(form)