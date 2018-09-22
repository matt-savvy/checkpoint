from django.contrib import admin
from runs.models import Run

class RunAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'race_entry', 'status', 'utc_time_ready', 'utc_time_due')

admin.site.register(Run, RunAdmin)