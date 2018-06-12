from django.core.management.base import BaseCommand, CommandError
from racers.models import Racer
from django.core.mail import send_mail, EmailMessage
from django.template import Context
from django.template.loader import get_template

class Command(BaseCommand):
    help = 'Emails all racers from before we had a t-shirt size field. '
    
    def handle(self, *args, **options):
        racers = Racer.objects.filter(id__lte=126).filter(paid=True)
        print racers.count()
        subject = "PHL NACCC : Update Required (fixed link)"
        headline = "We need your shirt size. (fixed link)"
        #self.stdout.write(unpaid_racers.count())

        for racer in racers:
            #print racer
            ctx = {'link' : racer.shirt_link, 'subject' : subject, 'headline' : headline}
            message = get_template('shirt_email.html').render(Context(ctx))
            msg = EmailMessage(subject, message, to=[racer.email])
            msg.content_subtype = 'html'
            msg.send()
            #self.stdout.write(racer.payment_link)
        
        