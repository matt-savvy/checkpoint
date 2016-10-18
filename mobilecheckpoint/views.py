from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from checkpoints.models import Checkpoint
from django.views.generic import ListView
from nacccusers.models import NACCCUser
from nacccusers.auth import AuthorizedRaceOfficalMixin

class MobileCheckpointControlView(TemplateView):
    template_name = 'checkpoint_control.html'
    
    def get_context_data(self, **kwargs):
        checkpoint = get_object_or_404(Checkpoint, pk=kwargs['pk'])
        context = {'checkpoint' : checkpoint}
        return context
        
class WorkerAuthorizedCheckpointView(TemplateView):
    template_name = 'auth_checkpoint_list.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['current_user'] = self.request.user
        return context
    
    