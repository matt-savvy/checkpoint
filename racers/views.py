from django.shortcuts import render
from django.views.generic import DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from util.photo import generate_small_image, generate_medium_image, generate_large_image
from django.core.files.storage import default_storage as storage
from django.core.files.base import ContentFile
import uuid
import os
from django.conf import settings
from racers.models import Racer
from racers.forms import RacerForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from nacccusers.auth import AuthorizedRaceOfficalMixin

class RacerListView(AuthorizedRaceOfficalMixin, ListView):
    model = Racer
    template_name = 'list_racers.html'
    context_object_name = 'racers'
    
    def get_queryset(self):
        return Racer.objects.all().order_by('racer_number')
    
class RacerDetailView(AuthorizedRaceOfficalMixin, DetailView):
    template_name = 'racer_detail.html'
    model = Racer

class RacerCreateView(AuthorizedRaceOfficalMixin, CreateView):
    template_name = 'create_racer.html'
    model = Racer
    form_class = RacerForm
    
    def get_success_url(self):
        messages.success(self.request, 'Racer was successfully created')
        if 'save-another' in self.request.POST:
            return '/racers/create/'
        return super(RacerCreateView, self).get_success_url()
    
class RacerUpdateView(AuthorizedRaceOfficalMixin, UpdateView):
    template_name = 'update_racer.html'
    model = Racer

class RacerDeleteView(AuthorizedRaceOfficalMixin, DeleteView):
    template_name = "delete_racer.html"
    model = Racer
    
    def get_success_url(self):
        messages.success(self.request, 'Racer was successfully deleted')
        return '/racers/'
