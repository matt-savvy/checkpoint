from django.shortcuts import render
from nacccusers.auth import AuthorizedRaceOfficalMixin
from checkpoints.models import Checkpoint
from companies.models import Company
from company_entries.models import CompanyEntry
from django.views.generic import TemplateView, RedirectView

class HomeView(RedirectView):
    permanent = False
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return '/racers/'

        company = Company.objects.filter(dispatcher=self.request.user).first()
        if company:
            company_entry = CompanyEntry.objects.filter(company=company)
            if company_entry:
                return '/dispatch/'

        return '/mobilecheckpoint/'

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
