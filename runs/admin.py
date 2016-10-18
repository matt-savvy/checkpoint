from django.contrib import admin
from runs.models import Run

class RunAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'race_entry', 'time_entered')

admin.site.register(Run, RunAdmin)