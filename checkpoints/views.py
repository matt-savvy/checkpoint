from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from nacccusers.auth import AuthorizedRaceOfficalMixin
from checkpoints.models import Checkpoint

class CheckpointListView(AuthorizedRaceOfficalMixin, ListView):
    model = Checkpoint
    template_name = 'list_checkpoints.html'
    context_object_name = 'checkpoints'
    
    def get_queryset(self):
        return Checkpoint.objects.all().order_by('checkpoint_name')
    
class CheckpointDetailView(AuthorizedRaceOfficalMixin, DetailView):
    template_name = 'checkpoint_detail.html'
    model = Checkpoint

class CheckpointCreateView(AuthorizedRaceOfficalMixin, CreateView):
    template_name = 'create_checkpoint.html'
    model = Checkpoint
    
class CheckpointUpdateView(AuthorizedRaceOfficalMixin, UpdateView):
    template_name = 'update_checkpoint.html'
    model = Checkpoint
    
class CheckpointDeleteView(AuthorizedRaceOfficalMixin, DeleteView):
    model = Checkpoint
    template_name = 'delete_checkpoint.html'
    success_url = '/checkpoints/'
