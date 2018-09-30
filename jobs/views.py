from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import View
from .forms import JobForm
from races.models import Manifest
import datetime
import pytz

from races.models import Race
from jobs.models import Job

class JobRaceListView(ListView):
    model = Job
    template_name = "jobs_race_select.html"
    context_object_name = 'jobs'
    
    def get_queryset(self):
        return Job.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(JobRaceListView, self).get_context_data(**kwargs)
        from django.db.models import Count
        
        races = Race.objects.annotate(num_jobs=Count('job'))

        context['races'] = races
        return context
    
class JobListView(ListView):
    model = Job
    template_name = 'list_jobs.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        return Job.objects.filter(race__pk=self.kwargs['race']).order_by('job_id')
    
class JobDetailView(DetailView):
    template_name = 'job_detail.html'
    model = Job

class JobCreateView(CreateView):
    template_name = 'create_job.html'
    model = Job
    form_class = JobForm
    
    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = self.initial.copy()
        race = self.request.GET.get('race')
        manifest = self.request.GET.get('manifest')
        if manifest:
            try:
                manifest = Manifest.objects.get(pk=manifest)
                initial['manifest'] = manifest
                initial['race'] = manifest.race
            except:
                pass
        elif race:
            try:
                race = Race.objects.get(pk=race)
                initial['race'] = race
            except:
                pass
        return initial
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        print form.cleaned_data['service']
        if form.cleaned_data['service'] == 'rush':
            self.object.points = Job.PAYOUT_RUSH
            self.object.minutes_due_after_start = Job.SERVICE_RUSH
        elif form.cleaned_data['service'] == 'double_rush':
            self.object.points = Job.PAYOUT_DOUBLE_RUSH
            self.object.minutes_due_after_start = Job.SERVICE_DOUBLE_RUSH
        else:
            self.object.points = Job.PAYOUT_REGULAR
            self.object.minutes_due_after_start = Job.SERVICE_REGULAR
        
        if self.object.manifest:
            if self.object.manifest.manifest_type == Manifest.TYPE_CHOICE_BONUS:
                self.object.points = str(1.5 * float(self.object.points))
        
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, 'Job was successfully created.')
        if 'save-another' in self.request.POST:
            if self.object.manifest:
                return '/jobs/create/?manifest={}'.format(self.object.manifest.pk)
            else:
                return '/jobs/create/?race={}'.format(self.object.race.pk)
        return super(JobCreateView, self).get_success_url()
    
class JobUpdateView(UpdateView):
    template_name = 'update_job.html'
    model = Job
    form_class = JobForm
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        if form.cleaned_data['service'] == 'rush':
            self.object.points = Job.PAYOUT_RUSH
            self.object.minutes_due_after_start = Job.SERVICE_RUSH
        elif form.cleaned_data['service'] == 'double_rush':
            self.object.points = Job.PAYOUT_DOUBLE_RUSH
            self.object.minutes_due_after_start = Job.SERVICE_DOUBLE_RUSH
        else:
            self.object.points = Job.PAYOUT_REGULAR
            self.object.minutes_due_after_start = Job.SERVICE_REGULAR

        if self.object.manifest:
            if self.object.manifest.manifest_type == Manifest.TYPE_CHOICE_BONUS:
                self.object.points = str(1.5 * float(self.object.points))
        
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
    
class JobDeleteView(DeleteView):
    model = Job
    template_name = 'delete_job.html'
    success_url = '/jobs/'

class JobCheckView(ListView):
    template_name="job_check.html"
    context_object_name = 'jobs'
    
    def get_queryset(self):
        race = Race.objects.get(pk=self.kwargs['race'])
        jobs = Job.objects.filter(race=race).order_by('job_id')
        timed_jobs = []
        for job in jobs:
            ready_time = race.race_start_time.astimezone(pytz.utc) + datetime.timedelta(minutes=job.minutes_ready_after_start)
            due_time = race.race_start_time.astimezone(pytz.utc) + datetime.timedelta(minutes=job.minutes_due_after_start)
            job_dict = {}
            job_dict['job_number'] = job.job_id
            job_dict['pick'] = job.pick_checkpoint
            job_dict['drop'] = job.drop_checkpoint
            job_dict['ready'] = ready_time.strftime('%m/%d %I:%M %p')
            job_dict['due'] = due_time.strftime('%m/%d %I:%M %p')
            job_dict['payout'] = job.points
            timed_jobs.append(job_dict)
        return timed_jobs
        
    
    
