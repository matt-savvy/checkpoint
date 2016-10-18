from django.shortcuts import render

from django.views.generic import TemplateView
from races.models import Race

class StreamerView(TemplateView):
    template_name = "streamer.html"
    
    def get_context_data(self, **kwargs):
        context = super(StreamerView, self).get_context_data(**kwargs)
        context['races'] = Race.objects.all()
        return context
