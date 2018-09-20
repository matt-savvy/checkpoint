from django.contrib import admin
from raceentries.models import RaceEntry
from django.utils import timezone
import pytz


def re_total(modealadmin, request, queryset):
    for entry in queryset:
        entry.add_up_runs()
        entry.add_up_points()
        entry.save()
re_total.short_description = u"Re-total Points"

class RaceEntryAdmin(admin.ModelAdmin):
    list_display = ('racer', 'get_racer_number','race', 'entry_status_as_string', 'due_back', 'number_of_runs_completed', 'grand_total')
    actions = [re_total]
    
    def due_back(self, obj):
        import datetime
        if obj.start_time:
            tz = pytz.timezone('US/Eastern')
            timezone.activate(tz)
            due_back = obj.start_time + datetime.timedelta(seconds=obj.race.time_limit * 60)
            return due_back
        else:
            return "N/A"
    
    def get_racer_number(self, obj):
        return obj.racer.racer_number
    get_racer_number.short_description = "Racer Number"
admin.site.register(RaceEntry, RaceEntryAdmin)
