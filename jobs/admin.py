from django.contrib import admin

from jobs.models import Job

class JobAdmin(admin.ModelAdmin):
    list_display = ('race','job_id', 'pick_checkpoint', 'drop_checkpoint', 'points')

admin.site.register(Job, JobAdmin)
