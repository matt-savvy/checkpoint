from django.core.management.base import BaseCommand, CommandError
from racers.models import Racer
from importlib import import_module
from ajax.serializers import RegistrationSerializer
from rest_framework.renderers import JSONRenderer
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore 
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
import pdb  

class Command(BaseCommand):
    help = 'Create a racer from session data.'
    
    def handle(self, *args, **options):
        
        sessions = Session.objects.all()
        
        if sessions:
            for session in sessions:
                decoded_data = session.get_decoded()
                if 'racer_json' in decoded_data:
                    stream = BytesIO(decoded_data['racer_json'])
                    racer_json = JSONParser().parse(stream)
                    print("{} {}".format(session.pk, racer_json))
            selection = raw_input("choose session number : ")
            #selection = "yatt6gr26ab5444z90h0gefeuro1r37b"
            try:
                sess = Session.objects.get(pk=selection)
                decoded_data = sess.get_decoded()
                stream = BytesIO(decoded_data['racer_json'])
                data = JSONParser().parse(stream)
                
                racer_first_name = data['first_name']
                racer_last_name = data['last_name']
                racer = Racer.objects.filter(first_name=racer_first_name).filter(last_name=racer_last_name).first()
                if racer:
                    print "existing racer found {}, {}".format(racer, racer.city)
                    you_sure = raw_input("are you sure? y / n").lower()
                    if you_sure != "y":
                        print "quitting"
                        return
                
                racer_number = int(data['racer_number'])
                while Racer.objects.filter(racer_number=racer_number).exists():
                    racer_number += 1
                data['racer_number'] = racer_number
                
                
                
                new_serializer = RegistrationSerializer(data=data)
                new_serializer.is_valid()
                
                if not new_serializer.is_valid():
                    print new_serializer.errors
                    return
                else:
                    new_racer = new_serializer.create(new_serializer.data)
                    
                print("{} {} {}".format(new_racer.racer_number, new_racer, new_racer.city))
                save = raw_input("save? y / n : ").lower()
                if save == "y":
                    paypal_tx = raw_input("enter paypal transaction ID number (if applicable): ")
                    new_racer.paypal_tx = paypal_tx
                    new_racer.paid = True
                    new_racer.save()
                    print "{} saved".format(new_racer)
                    sess.delete()
                else:
                    print("racer not saved!")
            except:
                print("some kind of error happened")