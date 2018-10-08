from django.shortcuts import render
from django.views.generic.edit import FormView
from racers.models import Racer
from .forms import ResultsForm
from raceentries.models import RaceEntry
from nacccusers.auth import AuthorizedRaceOfficalMixin

class ResultsGenerationView(AuthorizedRaceOfficalMixin, FormView):
    template_name = 'results_form.html'
    form_class = ResultsForm
    success_url = "/results/"

    def form_valid(self, form):
        race_entries = RaceEntry.objects.filter(race=form.cleaned_data['race']).filter(entry_status=RaceEntry.ENTRY_STATUS_FINISHED).order_by('-grand_total', 'last_action')
        racers_men = race_entries.filter(racer__gender=Racer.GENDER_MALE)
        racers_wtf = race_entries.exclude(racer__gender=Racer.GENDER_MALE)
        
        context = {
            'race'           : form.cleaned_data['race'],
            'race_entries_men' : self.place_racers(racers_men),
            'race_entries_wtf' : self.place_racers(racers_wtf),
            'show_dnf'       : form.cleaned_data['show_dnf'],
            'show_dq'        : form.cleaned_data['show_dq'],
        }
        
        if form.cleaned_data['cut_line'] != 0:
            context['show_cut'] = True
            context['cut_line'] = form.cleaned_data['cut_line']
            context['cut_remark'] = form.cleaned_data['cut_remark']
        else:
            context['show_cut'] = False
            
        if context['show_dnf']:
            context['dnf_racers'] = RaceEntry.objects.filter(race=form.cleaned_data['race']).filter(entry_status=RaceEntry.ENTRY_STATUS_DNF).order_by('racer__racer_number')
        
        if context['show_dq']:
            context['dq_racers'] = RaceEntry.objects.filter(race=form.cleaned_data['race']).filter(entry_status=RaceEntry.ENTRY_STATUS_DQD).order_by('racer__racer_number')
        
        return render(self.request, 'results.html', context)
    
    def place_racers(self, racers):
        if len(racers) == 0:
            return []
        
        results = []
        counter = 1
        first_run = True
        current_result_dict = {}
        for racer in racers:
            if first_run:
                current_result_dict = {
                    'place'     : counter,
                    'racers'    : [racer],
                    'earnings'  : racer.grand_total
                }
                first_run = False
            else:
                results.append(current_result_dict)
                counter += 1
                current_result_dict = {
                    'place'     : counter,
                    'racers'    : [racer],
                    'earnings'  : racer.grand_total
                }
        results.append(current_result_dict)
        return results
            
                
                
            
