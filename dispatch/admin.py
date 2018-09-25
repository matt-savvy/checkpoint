from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'race', 'race_entry', 'message_time', 'status', 'confirmed_time')
    
admin.site.register(Message, MessageAdmin)