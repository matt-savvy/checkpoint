from django.core.management.base import BaseCommand, CommandError
from racers.models import Racer
from django.core.mail import send_mail, EmailMessage
from django.template import Context
from django.template.loader import get_template

class Command(BaseCommand):
    help = 'Emails all racers where paid=False and provides them the payment link'
    
    def handle(self, *args, **options):
        unpaid_racers = Racer.objects.filter(paid=False)
        print unpaid_racers.count()
        subject = "PHL NACCC : Payment Required"
        headline = "We need you to settle up." 
        #self.stdout.write(unpaid_racers.count())
        
        for racer in unpaid_racers:
            print racer
            ctx = {'link' : racer.payment_link, 'subject' : subject, 'headline' : headline}
            message = get_template('unpaid_racer_email.html').render(Context(ctx))
            msg = EmailMessage(subject, message, to=[racer.email])
            msg.content_subtype = 'html'
            msg.send()

        
        