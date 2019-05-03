from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from nacccusers.auth import AuthorizedRaceOfficalMixin
from races.models import Race, Manifest
from races.forms import RaceForm

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

class ManifestListView(AuthorizedRaceOfficalMixin, ListView):
    model = Manifest
    template_name = 'list_manifests.html'
    context_object_name = 'manifests'

class ManifestDetailView(AuthorizedRaceOfficalMixin, DetailView):
    template_name = 'manifest_detail.html'
    model = Manifest

class ManifestCreateView(AuthorizedRaceOfficalMixin, CreateView):
    template_name = 'create_manifest.html'
    model = Manifest

class ManifestUpdateView(AuthorizedRaceOfficalMixin, UpdateView):
    template_name = 'update_manifest.html'
    model = Manifest

class ManifestDeleteView(AuthorizedRaceOfficalMixin, DeleteView):
    model = Manifest
    template_name = 'delete_manifest.html'
    success_url = '/races/manifests/'
