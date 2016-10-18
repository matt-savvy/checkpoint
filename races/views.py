from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from nacccusers.auth import AuthorizedRaceOfficalMixin

from races.models import Race

class RaceListView(AuthorizedRaceOfficalMixin, ListView):
    model = Race
    template_name = 'list_races.html'
    context_object_name = 'races'
    
class RaceDetailView(AuthorizedRaceOfficalMixin, DetailView):
    template_name = 'race_detail.html'
    model = Race

class RaceCreateView(AuthorizedRaceOfficalMixin, CreateView):
    template_name = 'create_race.html'
    model = Race
    
class RaceUpdateView(AuthorizedRaceOfficalMixin, UpdateView):
    template_name = 'update_race.html'
    model = Race
    
class RaceDeleteView(AuthorizedRaceOfficalMixin, DeleteView):
    model = Race
    template_name = 'delete_race.html'
    success_url = '/races/'
