from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.views.generic import View
import datetime
import pytz

from races.models import Race
from jobs.models import Job

class JobRaceListView(ListView):
    model = Job
    template_name = "jobs_race_select.html"
    context_object_name = 'jobs'
    
    def get_queryset(self):
        return Job.objects.all().distinct('race')
    
    def get_context_data(self, **kwargs):
        context = super(JobRaceListView, self).get_context_data(**kwargs)
        races_in_jobs = Job.objects.all().distinct('race')
        job_counts = []
        for race in races_in_jobs:
            count = Job.objects.filter(race=race.race).count()
            job_counts.append(count)
        for x in range(0, len(context['jobs'])):
            context['jobs'][x].job_counts = job_counts[x]
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
    
    def get_success_url(self):
        messages.success(self.request, 'Job was successfully created.')
        if 'save-another' in self.request.POST:
            return '/jobs/create/'
        return super(JobCreateView, self).get_success_url()
    
class JobUpdateView(UpdateView):
    template_name = 'update_job.html'
    model = Job
    
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
        
    
    
