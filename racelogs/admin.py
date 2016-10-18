from django.contrib import admin
from .models import RaceLog

class RaceLogAdmin(admin.ModelAdmin):
    list_display = ('entered','racer','race','user','log','current_grand_total','current_number_of_runs')

admin.site.register(RaceLog, RaceLogAdmin)