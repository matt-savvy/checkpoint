from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from checkpoints.models import Checkpoint
from django.views.generic import ListView
from racecontrol.models import RaceControl
from nacccusers.models import NACCCUser
from nacccusers.auth import AuthorizedRaceOfficalMixin
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

class MobileCheckpointControlView(TemplateView):
    template_name = 'checkpoint_control_react.html'
    
    method_decorator(ensure_csrf_cookie)
    def render_to_response(self, context, **response_kwargs):
        response = super(MobileCheckpointControlView, self).render_to_response(context, **response_kwargs)
        checkpoint = get_object_or_404(Checkpoint, pk=self.kwargs['pk'])
        current_race = RaceControl.shared_instance().current_race
        response.set_cookie('checkpointID', checkpoint.pk)
        response.set_cookie('raceID', current_race.pk)
        return response
    
    def get_context_data(self, **kwargs):
        checkpoint = get_object_or_404(Checkpoint, pk=kwargs['pk'])
        context = {'checkpoint' : checkpoint}
        return context
        
class MobileCheckpointControlLegacyView(TemplateView):
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
    
    