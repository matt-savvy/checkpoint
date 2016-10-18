from django.contrib import admin
from racers.models import Racer

class RacerAdmin(admin.ModelAdmin):
    list_display = ('racer_number', 'first_name', 'last_name', 'gender', 'category')

admin.site.register(Racer, RacerAdmin)