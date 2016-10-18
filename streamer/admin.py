from django.contrib import admin
from .models import StreamEvent

class StreamEventAdmin(admin.ModelAdmin):
    list_display = ('race', 'timestamp', 'racer', 'message', 'published')

admin.site.register(StreamEvent, StreamEventAdmin)
