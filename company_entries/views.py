from django.shortcuts import render
from .models import CompanyEntry
from companies.models import Company
from races.models import Race

class ManageCompanyEntryView(AuthorizedRaceOfficalMixin, TemplateView):
    template_name = 'manage_race_entries.html'

    def get_context_data(self, **kwargs):
        context = super(ManageRaceEntryView, self).get_context_data(**kwargs)
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        context['race'] = race

        race_entries = RaceEntry.objects.filter(race=race)
        context['race_entries'] = race_entries

        racers = Racer.objects.all()
        not_in_race = []

        #Seems rather un-pythonic. Must be a faster way?
        for racer in racers:
            found = False
            for entry in race_entries:
                if entry.racer == racer:
                    found = True
                    break
            if not found:
                not_in_race.append(racer)
        context['not_in_race'] = not_in_race
        return context
