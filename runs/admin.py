from django.contrib import admin
from runs.models import Run

class RunAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'race_entry', 'status', 'time_entered', 'utc_time_ready')

admin.site.register(Run, RunAdmin)