from django.shortcuts import render
from nacccusers.auth import AuthorizedRaceOfficalMixin

from django.views.generic import TemplateView

class HomeView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "home.html"

class WelcomeView(TemplateView):
    template_name = "welcome.html"
    
class ScheduleView(TemplateView):
    template_name = "schedule.html"

class ContactView(TemplateView):
    template_name = "contact.html"
    
class EmailTemplate(TemplateView):
    template_name = "email.html"

class WhatIsView(TemplateView):
    template_name = "what_is_naccc.html"