from django.contrib import admin

from jobs.models import Job

class JobAdmin(admin.ModelAdmin):
    list_display = ('race','job_id',  'minutes_ready_after_start',  'pick_checkpoint', 'drop_checkpoint', 'points')

admin.site.register(Job, JobAdmin)
