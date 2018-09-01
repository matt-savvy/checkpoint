from django.core.management.base import BaseCommand, CommandError
from racers.models import Racer
from importlib import import_module
from ajax.serializers import RegistrationSerializer
from rest_framework.renderers import JSONRenderer
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore 
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
import csv
import pdb  

class Command(BaseCommand):
    help = "Make a mailing list of only people who have not registered but did sign up."
    
    def handle(self, *args, **options):
        racers = Racer.objects.filter(paid=True)
        new_list = []
        reg_list = []
        
        with open('registered_list.csv', 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                email = row['Email Address']
                reg_list.append(email)
        
        with open('mailing_list.csv', 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                email = row['Email Address']
                #if not racers.filter(email=email).exists():
                if not email in reg_list:
                    new_list.append(email)
        
        for email in new_list:
            print email
            
        return
        
        