from django.contrib import admin
from .models import Checkpoint

class CheckpointAdmin(admin.ModelAdmin):
    list_display = ('checkpoint_number','checkpoint_name')

admin.site.register(Checkpoint, CheckpointAdmin)

# Register your models here.
