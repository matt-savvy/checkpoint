from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import TemplateView
from .models import RaceEvent, RaceLog

class RaceLogListView(ListView):
    model = RaceLog
    template_name = "list_race_logs.html"
    context_object_name = 'logs'
    
    def get_queryset(self):
        return RaceLog.objects.filter(racer__racer_number=self.kwargs['racer']).order_by('entered')

class RaceEventListView(ListView):
    model = RaceEvent
    template_name = "list_race_events.html"
    context_object_name = 'racers'
    
    def get_queryset(self):
        return RaceEvent.objects.filter(minute=self.kwargs['minute']).order_by('-points', 'racer__racer_number')
        
class PlaybackView(TemplateView):
    template_name = 'playback.html'