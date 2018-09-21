from django.core.management.base import BaseCommand, CommandError
from racers.models import Volunteer
from importlib import import_module
from ajax.serializers import RegistrationSerializer
from rest_framework.renderers import JSONRenderer
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore 
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
import pdb  

class Command(BaseCommand):
    help = 'Create a volunteer from session data.'
    
    def handle(self, *args, **options):
        
        sessions = Session.objects.all()
        
        if sessions:
            for session in sessions:
                decoded_data = session.get_decoded()
                if 'volunteer_json' in decoded_data:
                    stream = BytesIO(decoded_data['volunteer_json'])
                    volunteer_json = JSONParser().parse(stream)
                    print("{} {}".format(session.pk, volunteer_json))
            selection = raw_input("choose session number : ")
            try:
                sess = Session.objects.get(pk=selection)
                decoded_data = sess.get_decoded()
                stream = BytesIO(decoded_data['volunteer_json'])
                data = JSONParser().parse(stream)
                
                volunteer_first_name = data['first_name']
                volunteer_last_name = data['last_name']
                volunteer = Volunteer.objects.filter(first_name=volunteer_first_name).filter(last_name=volunteer_last_name).first()
                if volunteer:
                    print "existing volunteer found {}, {}".format(volunteer, volunteer.city)
                    you_sure = raw_input("are you sure? y / n").lower()
                    if you_sure != "y":
                        print "quitting"
                        return
                
                new_serializer = VolunteerSerializer(data=data)
                new_serializer.is_valid()
                
                if not new_serializer.is_valid():
                    print new_serializer.errors
                    return
                else:
                    new_volunteer = new_serializer.create(new_serializer.data)
                    
                print("{} {} {}".format(new_volunteer, new_volunteer.city))
                save = raw_input("save? y / n : ").lower()
                if save == "y":
                    paypal_tx = raw_input("enter paypal transaction ID number (if applicable): ")
                    new_volunteer.paypal_tx = paypal_tx
                    new_volunteer.paid = True
                    new_volunteer.save()
                    print "{} saved".format(new_volunteer)
                    sess.delete()
                else:
                    print("volunteer not saved!")
            except:
                print("some kind of error happened")