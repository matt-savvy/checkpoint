from django.shortcuts import render
from nacccusers.auth import AuthorizedRaceOfficalMixin

from django.views.generic import TemplateView, RedirectView

class HomeView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "home.html"

class WelcomeView(RedirectView):
    permanent = True
    url = 'https://naccc2018.com/'
    
class ScheduleView(TemplateView):
    template_name = "schedule.html"

class ContactView(TemplateView):
    template_name = "contact.html"
    
class EmailTemplate(TemplateView):
    template_name = "email.html"

class WhatIsView(TemplateView):
    template_name = "what_is_naccc.html"