from django.shortcuts import render
from nacccusers.auth import AuthorizedRaceOfficalMixin

from django.views.generic import TemplateView

class HomeView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = "home.html"
