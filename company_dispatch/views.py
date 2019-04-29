from django.views.generic import DetailView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden
from ajax.serializers import CompanyEntrySerializer, RaceEntrySerializer
from companies.models import Company
from company_entries.models import CompanyEntry
from racecontrol.models import RaceControl
from json import dumps

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
        rc = RaceControl.shared_instance()
        race = rc.current_race
        return CompanyEntry.objects.filter(company=self.company).filter(race=race).first()

    def get_context_data(self, **kwargs):
        #import pdb; pdb.set_trace()
        """get the initial data"""
        context = super(CompanyDispatchView, self).get_context_data(**kwargs)
        serializer = CompanyEntrySerializer(self.object)
        context['company_entry'] = dumps(serializer.data)
        #entries = self.object.get_race_entries()
        #race_entry_serializer = RaceEntrySerializer(entries, many=True)
        #context['race_entries'] = dumps(race_entry_serializer.data)
        return context
