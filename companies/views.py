from django.views.generic import CreateView, UpdateView, ListView, DetailView
from nacccusers.auth import AuthorizedRaceOfficalMixin
from django.contrib import messages
from .models import Company
from .forms import CompanyForm
from company_entries.models import CompanyEntry
from racecontrol.models import RaceControl
from nacccusers.models import NACCCUser

class CompanyCreateView(AuthorizedRaceOfficalMixin, CreateView):
    model = Company
    template_name = "companies/create_company.html"
    success_url = "/companies/"

    def form_valid(self, form):
        self.object = form.save()
        rc = RaceControl.shared_instance()
        race = rc.current_race
        if not CompanyEntry.objects.filter(company=self.object).filter(race=race).exists():
            company_entry = CompanyEntry(company=self.object, race=race)
            company_entry.save()
        messages.success(self.request, "{} added.".format(self.object.name))
        return super(CompanyCreateView, self).form_valid(form)

class CompanyDetailView(AuthorizedRaceOfficalMixin, DetailView):
    model = Company
    template_name = "companies/company_detail.html"

class CompanyUpdateView(AuthorizedRaceOfficalMixin, UpdateView):
    model = Company
    template_name = "companies/create_company.html"

class CompanyListView(AuthorizedRaceOfficalMixin, ListView):
    model = Company
    queryset = Company.objects.all()
    context_object_name = "companies"
    template_name = "companies/list_company.html"
