from django.shortcuts import render
from django.views.generic import FormView
from django.contrib import messages
from nacccusers.auth import AuthorizedRaceOfficalMixin
from .models import CompanyEntry
from .forms import CompanyEntryForm
from companies.models import Company
from races.models import Race
from racelogs.models import RaceLog
from racecontrol.models import RaceControl

class CompanyEntryFinishView(AuthorizedRaceOfficalMixin, FormView):
    form_class = CompanyEntryForm
    template_name = "company_entries/form.html"
    success_url = "/dispatch/finish/"

    def get_form(self, form_class):
        form = super(CompanyEntryFinishView, self).get_form(form_class)
        rc = RaceControl.shared_instance()
        form.fields['company_entry'].queryset = CompanyEntry.objects.filter(race=rc.current_race).filter(entry_status=CompanyEntry.ENTRY_STATUS_RACING)
        return form

    def form_valid(self, form):
        company_entry = form.cleaned_data['company_entry']

        if company_entry.entry_status == CompanyEntry.ENTRY_STATUS_RACING:
            ##finish all the racers at this company
            for race_entry in company_entry.get_race_entries():
                if race_entry.finish_racer():
                    race_entry.save()
                    RaceLog(racer=race_entry.racer, race=race_entry.race, user=self.request.user, log="Racer finished race.", current_grand_total=race_entry.grand_total, current_number_of_runs=race_entry.number_of_runs_completed).save()
            #finish the company_entry
            if company_entry.finish():
                company_entry.save()
                messages.success(self.request, '{} finished!'.format(company_entry.company.name))
        else:
            messages.warning(self.request, 'ERROR: {} either already finished or never started!'.format(company_entry.company.name))

        return super(CompanyEntryFinishView, self).form_valid(form)
