from django.contrib import admin
from raceentries.models import RaceEntry

def re_total(modealadmin, request, queryset):
    for entry in queryset:
        entry.add_up_runs()
        entry.add_up_points()
        entry.save()
re_total.short_description = u"Re-total Points"

class RaceEntryAdmin(admin.ModelAdmin):
    list_display = ('racer', 'get_racer_number','race', 'entry_status_as_string', 'number_of_runs_completed', 'grand_total')
    actions = [re_total]
    
    def get_racer_number(self, obj):
        return obj.racer.racer_number
    get_racer_number.short_description = "Racer Number"
admin.site.register(RaceEntry, RaceEntryAdmin)
