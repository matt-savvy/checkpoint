from .models import Message
import datetime

def get_next_message(race):
    right_now = datetime.datetime.now()
    
    message = Message.objects.filter(confirmed=False).filter(message_time__lte=right_now).first()
    return message
    