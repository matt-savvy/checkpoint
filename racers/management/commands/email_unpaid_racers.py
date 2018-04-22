from django.core.management.base import BaseCommand, CommandError
from racers.models import Racer
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Emails all racers where paid=False and provides them the payment link'
    
    def handle(self, *args, **options):
        unpaid_racers = Racer.objects.filter(paid=False)
        print unpaid_racers.count()
        #self.stdout.write(unpaid_racers.count())
        
        for racer in unpaid_racers:
            print racer.payment_link
            #self.stdout.write(racer.payment_link)
        
        