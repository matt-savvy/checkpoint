from django.views.generic import DetailView, FormView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden
from nacccusers.auth import AuthorizedRaceOfficalMixin
from ajax.serializers import CompanyEntrySerializer, RaceEntrySerializer
from companies.models import Company
from company_entries.models import CompanyEntry
from company_entries.forms import CompanyEntryForm
from racecontrol.models import RaceControl
from runs.models import RunChangeLog
from races.models import Race
from json import dumps
from django.core.serializers.json import DjangoJSONEncoder


class CompanyScoreboard(DetailView):
    model = Race
    template_name = 'company_dispatch/dispatch.html'

    method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return HttpResponseForbidden()
        return super(CompanyScoreboard, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        rc = RaceControl.shared_instance()
        race = rc.current_race
        return race

    def get_context_data(self, **kwargs):
        """get the initial data"""
        context = super(CompanyScoreboard, self).get_context_data(**kwargs)
        company_entries = CompanyEntry.objects.filter(race=self.object)
        company_entry_serializer = CompanyEntrySerializer(company_entries, many=True)
        context['init'] = dumps(company_entry_serializer.data, cls=DjangoJSONEncoder)
        changelogs = RunChangeLog.objects.order_by('pk')
        if changelogs:
            context['head'] = changelogs.last().pk
        else:
            context['head'] = 0
        context['js_file'] = 'company_scoreboard'
        return context


class CompanyDispatchView(DetailView):
    model = CompanyEntry
    queryset = CompanyEntry.objects.all()
    template_name = 'company_dispatch/dispatch.html'

    method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        try:
            self.company = Company.objects.get(dispatcher=request.user)
        except:
            return HttpResponseForbidden()
        return super(CompanyDispatchView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        company_entry_pk = self.request.GET.get('company_entry')
        if company_entry_pk and self.request.user.is_superuser:
            print("company_entry_pk", company_entry_pk)
            return CompanyEntry.objects.get(pk=company_entry_pk)
        rc = RaceControl.shared_instance()
        race = rc.current_race
        return CompanyEntry.objects.filter(company=self.company).filter(race=race).first()

    def get_context_data(self, **kwargs):
        """get the initial data"""
        context = super(CompanyDispatchView, self).get_context_data(**kwargs)
        serializer = CompanyEntrySerializer(self.object)
        context['init'] = dumps(serializer.data, cls=DjangoJSONEncoder)
        changelogs = RunChangeLog.objects.filter(company_pk=self.object.pk).order_by('pk')
        if changelogs:
            context['head'] = changelogs.last().pk
        else:
            context['head'] = 0

        context['js_file'] = 'company_dispatch'
        #entries = self.object.get_race_entries()
        #race_entry_serializer = RaceEntrySerializer(entries, many=True)
        #context['race_entries'] = dumps(race_entry_serializer.data)
        return context

class CompanyEntrySelectView(AuthorizedRaceOfficalMixin, FormView):
    form_class = CompanyEntryForm
    template_name = "company_dispatch/select_form.html"
