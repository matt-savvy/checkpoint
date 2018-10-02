from django.shortcuts import render
from django.views.generic import DeleteView
from django.views.generic.base import View, TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from util.photo import generate_small_image, generate_medium_image, generate_large_image
from django.core.files.storage import default_storage as storage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse, reverse_lazy
import uuid
import os
from django.conf import settings
from racers.models import Racer, Volunteer
from racers.forms import RacerForm, RegisterForm, ShirtForm, VolunteerForm, PickupForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from nacccusers.auth import AuthorizedRaceOfficalMixin
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.utils.decorators import method_decorator
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.views.decorators.http import require_GET
import hashlib
import pdb
from rest_framework.renderers import JSONRenderer
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore 
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from django.db.models import Q
from django.contrib import messages

class RacerListView(AuthorizedRaceOfficalMixin, ListView):
    model = Racer
    template_name = 'list_racers.html'
    context_object_name = 'racers'
    
    def get_context_data(self, **kwargs):
        context = super(RacerListView, self).get_context_data(**kwargs)
        queryset = context['object_list']
        context['include_unpaid'] = self.request.GET.get('include_unpaid') == 'True'
        context['total_men'] = len(queryset.filter(gender='M'))
        context['total_wtf'] = len(queryset.filter(Q(gender='F') | Q(gender='T')))
        context['total_women'] = len(queryset.filter(gender='F'))
        context['total_trans'] = len(queryset.filter(gender='T'))
        
        context['total_mess'] = len(queryset.filter(category=0))
        context['total_non'] = len(queryset.filter(category=1))
        context['total_ex'] = len(queryset.filter(category=2))
        
        context['total_s'] = len(queryset.filter(shirt_size='S'))
        context['total_m'] = len(queryset.filter(shirt_size='M'))
        context['total_l'] = len(queryset.filter(shirt_size='L'))
        context['total_xl'] = len(queryset.filter(shirt_size='XL'))
        context['total_unpaid'] = len(queryset.filter(paid=False))
        
        return context
    
    def get_queryset(self):
        include_unpaid = self.request.GET.get('include_unpaid') == 'True'
        queryset = Racer.objects.order_by('-pk')
        if not include_unpaid:
            queryset = queryset.filter(paid=True)
        return queryset

class RacerListViewPublic(ListView):
    model = Racer
    template_name = 'list_racers_public.html'
    context_object_name = 'racers'
    
    def get_queryset(self):
        return Racer.objects.filter(paid=True)
        
    def get_context_data(self, **kwargs):
        context = super(RacerListViewPublic, self).get_context_data(**kwargs)
        racers = context['object_list']
        racers = list(racers)
        for racer in racers:
            racer.racer_number = int(racer.racer_number)
        racers = list(racers)
        racers.sort(key=lambda x: x.racer_number)
        print racers
        context['racers'] = racers
        return context

class RacerDetailView(AuthorizedRaceOfficalMixin, DetailView):
    template_name = 'racer_detail.html'
    model = Racer

from importlib import import_module
from django.conf import settings
from ajax.serializers import RegistrationSerializer, VolunteerSerializer
from paypal.standard.pdt.views import process_pdt
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from django.contrib.sessions.models import Session
from rest_framework.renderers import JSONRenderer
from django.contrib.sessions.backends.db import SessionStore            

class ThankYouView(TemplateView):
    template_name = "thank_you.html"

@require_GET
def RegFinished(request):
    pdt_obj, failed = process_pdt(request)
    context = {"failed": failed, "pdt_obj": pdt_obj}
    if not failed:
        if pdt_obj.receiver_email == settings.PAYPAL_RECEIVER_EMAIL:
            session_key = pdt_obj.custom
            if session_key:
                SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        
                s = Session.objects.get(pk=session_key)    
                decoded_data = s.get_decoded()

                stream = BytesIO(decoded_data['racer_json'])
                data = JSONParser().parse(stream)
                
                racer_number = int(data['racer_number'])
                while Racer.objects.filter(racer_number=racer_number).exists():
                    racer_number += 1
                data['racer_number'] = racer_number
                
                new_serializer = RegistrationSerializer(data=data)
                new_serializer.is_valid()
                
                new_racer = new_serializer.create(new_serializer.data)
                new_racer.paid = True
                new_racer.paypal_tx = pdt_obj.txn_id
                new_racer.save()
                s.delete()
                
                if 'session_key' in request:    
                    del request.session['session_key']
                    
            else:
                try:
                    racer_number = pdt_obj.item_name.split("Racer ")[1]
                    racer = Racer.objects.get(racer_number=racer_number)
                    racer.mark_as_paid()
                    redirect_url = "{}?pk={}&racer_number={}".format(reverse('shirt-view'), str(racer.pk), racer_number)
                    return HttpResponseRedirect(redirect_url)
                except:
                    return render(request, 'bad_payment.html', context)
                
            return HttpResponseRedirect(reverse('thank-you'))
    return render(request, 'bad_payment.html', context)

def view_that_asks_for_money(request):
    racer_number = request.GET.get('racer_number')
    session_key = request.session.get('session_key')
    if racer_number:
        url = request.build_absolute_uri(reverse('pay-view'))
        cancel_url = url + "?racer_number={}".format(racer_number)
    else:
        racer_number = ''
        cancel_url = request.build_absolute_uri(reverse('welcome-view'))

    racer = Racer.objects.filter(racer_number=racer_number).first()
    if racer:
        if racer.paid:
            return render(request, 'thank_you.html')
    
    item_name = "Registration for Racer {}".format(str(racer_number))    
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": settings.REGISTRATION_PRICE,
        "item_name": item_name,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        #"notify_url": "http://92105408.ngrok.io/paypal/", 
        #"return_url" : "http://92105408.ngrok.io/racers/pdtreturn/",
        "return_url": request.build_absolute_uri(reverse('pdt_return_url')),
        "cancel_return": cancel_url,
        "custom" : session_key,
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    context['registration_price'] = settings.REGISTRATION_PRICE
    return render(request, 'racer_pay.html', context)

@csrf_exempt
def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    print "show_me_the_money"
    print ipn_obj
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email == settings.PAYPAL_RECEIVER_EMAIL:
            
            try:
                session_key = ipn_obj.custom
                SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
                s = Session.objects.get(pk=session_key)    
                decoded_data = s.get_decoded()
                stream = BytesIO(decoded_data['racer_json'])
                data = JSONParser().parse(stream)
            
                new_serializer = RegistrationSerializer(data=data)
                new_serializer.is_valid()
                new_racer = new_serializer.create(new_serializer.data)
                new_racer.paid = True
                new_racer.paypal_tx = pdt_obj.txn_id
                new_racer.save()
                s.delete()
            except:
                pass
        else:
            return
    else:
        pass

class RacerRegisterView(CreateView):
    template_name = 'register_racer.html'
    model = Racer
    form_class = RegisterForm
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(RacerRegisterView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
          context = super(RacerRegisterView, self).get_context_data(**kwargs)
          context['registration_price'] = settings.REGISTRATION_PRICE
          return context
    
    def form_valid(self, form):
        if 'session_key' in self.request:
            del request.session['session_key']
            s.delete()
        self.object = form.save(commit=False)
        serializer = RegistrationSerializer(self.object)
        json = JSONRenderer().render(serializer.data)
        s = SessionStore()
        s['racer_json'] = json
        s.create()
        self.request.session['session_key'] = s.session_key
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        url = self.request.build_absolute_uri(reverse('pay-view'))
        try:
            racer_number = self.object.racer_number
            url = url + "?racer_number={}".format(str(racer_number))
        except:
            pass
        return url

class RacerCreateView(AuthorizedRaceOfficalMixin, CreateView):
    template_name = 'create_racer.html'
    model = Racer
    form_class = RacerForm
    
    def get_success_url(self):
        messages.success(self.request, 'Racer was successfully created')
        if 'save-another' in self.request.POST:
            return '/racers/create/'
        return super(RacerCreateView, self).get_success_url()
    
class RacerUpdateView(AuthorizedRaceOfficalMixin, UpdateView):
    template_name = 'update_racer.html'
    model = Racer
    
    def get_success_url(self):
       import requests
       MAILCHIMP_USERNAME = 'naccc2018'
       MAILCHIMP_API_KEY = '73e4693f5ed7ff2cd92e3b35a5abf0f1-us16' 
       mailchimp_user = '{}:{}'.format(MAILCHIMP_USERNAME, MAILCHIMP_API_KEY)
       md5 = hashlib.md5(self.object.email).hexdigest()
       listid = '459031a70e'
       address = 'https://us16.api.mailchimp.com/3.0'
       endpoint =  "{}/lists/{}?user={}:{}".format(address, listid, MAILCHIMP_USERNAME, MAILCHIMP_API_KEY)
       response = requests.get(address, headers={'user' : mailchimp_user})
       print response.json()['detail']
       pass
       return super(RacerUpdateView, self).get_success_url()

class RacerUpdateShirtView(UpdateView):
    template_name = 'update_racer_shirt.html'
    model = Racer
    fields = ['shirt_size']
    
    def get_success_url(self):
        messages.success(self.request, 'Racer updated.')
        return reverse_lazy('thank-you')
    
    def get_object(self):
        racer_pk = self.request.GET.get('pk')
        racer_number = self.request.GET.get('racer_number')
        return get_object_or_404(Racer, pk=racer_pk, racer_number=racer_number)
    
    
class RacerDeleteView(AuthorizedRaceOfficalMixin, DeleteView):
    template_name = "delete_racer.html"
    model = Racer
    
    def get_success_url(self):
        messages.success(self.request, 'Racer was successfully deleted')
        return '/racers/'

class SessionListView(AuthorizedRaceOfficalMixin, ListView):
    model = Session
    template_name = "list_sessions.html"
    
    def get_context_data(self, **kwargs):
        context = super(SessionListView, self).get_context_data(**kwargs)
        
        object_list = []
        sessions = Session.objects.all()
        if sessions:
            for session in sessions:
                decoded_data = session.get_decoded()
                if 'racer_json' in decoded_data:
                    stream = BytesIO(decoded_data['racer_json'])
                    racer_json = JSONParser().parse(stream)
                    obj = session
                    obj.racer_json = racer_json
                    object_list.append(obj)
        context['object_list'] = object_list
        return context

class NumbersListView(AuthorizedRaceOfficalMixin, ListView):
    model = Racer
    template_name = "list_racer_numbers.html"
    
    def get_context_data(self, **kwargs):
        context = super(NumbersListView, self).get_context_data(**kwargs)        
        existing_numbers = list(Racer.objects.values_list('racer_number', flat=True).order_by('racer_number'))
        
        racer_numbers = range(500, 1000)
        racer_numbers.insert(0, 89)
        racer_numbers.insert(0, 748)
        
        numbers_to_add = 300 - len(existing_numbers)
        existing_numbers = [int(x) for x in existing_numbers]

        available_numbers = [x for x in racer_numbers if x not in existing_numbers][:numbers_to_add]
        numbers_to_order = existing_numbers + available_numbers
        numbers_to_order.sort()
        print len(numbers_to_order)

        context['numbers'] = numbers_to_order 
        return context
        
class EmailListView(AuthorizedRaceOfficalMixin, ListView):
    model = Racer
    template_name = "list_emails.html"
    
class VolunteerRegisterView(CreateView):
    template_name = 'register_volunteer.html'
    model = Volunteer
    form_class = VolunteerForm
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(VolunteerRegisterView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
          context = super(VolunteerRegisterView, self).get_context_data(**kwargs)
          context['volunteer_price'] = settings.VOLUNTEER_PRICE
          return context
    
    def form_valid(self, form):
        if 'session_key' in self.request:
            del request.session['session_key']
            s.delete()
        self.object = form.save(commit=False)
        serializer = VolunteerSerializer(self.object)
        json = JSONRenderer().render(serializer.data)
        s = SessionStore()
        s['volunteer_json'] = json
        s.create()
        self.request.session['session_key'] = s.session_key
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        url = self.request.build_absolute_uri(reverse('volunteer-pay-view'))
        try:
            url = url + "?first_name={}&last_name={}".format(self.object.first_name, self.object.last_name)
        except:
            pass
        return url
        
def volunteer_view_that_asks_for_money(request):
    first_name = request.GET.get('first_name')
    last_name = request.GET.get('last_name')
    volunteer_name = "{} {}".format(first_name, last_name)
    session_key = request.session.get('session_key')
    if volunteer_name:
        url = request.build_absolute_uri(reverse('volunteer-pay-view'))
        cancel_url = url + "?first_name={}&last_name={}".format(first_name, last_name)
    else:
        volunteer_name = ''
        cancel_url = request.build_absolute_uri(reverse('welcome-view'))

    volunteer = Volunteer.objects.filter(first_name=first_name).filter(last_name=last_name).first()
    if volunteer:
        if volunteer.paid:
            return render(request, 'thank_you.html')
    
    item_name = "Registration for Volunteer {}".format(str(volunteer_name))    
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": settings.VOLUNTEER_PRICE,
        "item_name": item_name,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        #"notify_url": "http://92105408.ngrok.io/paypal/", 
        #"return_url" : "http://92105408.ngrok.io/racers/pdtreturn/",
        "return_url": request.build_absolute_uri(reverse('volunteer-pdt_return_url')),
        "cancel_return": cancel_url,
        "custom" : session_key,
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    context['volunteer_price'] = settings.VOLUNTEER_PRICE
    return render(request, 'volunteer_pay.html', context)
    
@require_GET
def VolunteerRegFinished(request):
    pdt_obj, failed = process_pdt(request)
    context = {"failed": failed, "pdt_obj": pdt_obj}
    if not failed:
        if pdt_obj.receiver_email == settings.PAYPAL_RECEIVER_EMAIL:
            session_key = pdt_obj.custom
            if session_key:
                SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        
                s = Session.objects.get(pk=session_key)    
                decoded_data = s.get_decoded()

                stream = BytesIO(decoded_data['volunteer_json'])
                data = JSONParser().parse(stream)
                
                first_name = data['first_name']
                last_name = data['last_name']
                
                new_serializer = VolunteerSerializer(data=data)
                new_serializer.is_valid()
                
                new_volunteer = new_serializer.create(new_serializer.data)
                new_volunteer.paid = True
                new_volunteer.paypal_tx = pdt_obj.txn_id
                new_volunteer.save()
                s.delete()
                
                if 'session_key' in request:    
                    del request.session['session_key']
                
            return HttpResponseRedirect(reverse('thank-you'))
    return render(request, 'bad_payment.html', context)
    
class VolunteerListView(AuthorizedRaceOfficalMixin, ListView):
    model = Volunteer
    template_name = "volunteer_list.html"
    
    def get_context_data(self, **kwargs):
        context = super(VolunteerListView, self).get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['total_s'] = len(queryset.filter(shirt_size='S'))
        context['total_m'] = len(queryset.filter(shirt_size='M'))
        context['total_l'] = len(queryset.filter(shirt_size='L'))
        context['total_xl'] = len(queryset.filter(shirt_size='XL'))
        
        return context
    
class VolunteerDetailView(AuthorizedRaceOfficalMixin, DetailView):
    model = Volunteer
    template_name = "volunteer_detail.html"
    
class VolunteerEmailsListView(AuthorizedRaceOfficalMixin, ListView):
    model = Volunteer
    template_name = "list_emails.html"

class RacerPacketPickupView(AuthorizedRaceOfficalMixin, UpdateView):
    model = Racer
    form_class = PickupForm
    template_name = "update_racer.html"
    
    def form_valid(self, form):
        self.object = form.save()
        if self.object.cargo:
            self.object.heat = Racer.HEAT_FIRST
            
        self.object.packet = True
        self.object.save()
        
        messages.success(self.request, 'Racer has been logged, packet picked up!')    
        return HttpResponseRedirect(self.get_success_url())

class VolunteerPacketPickupView(AuthorizedRaceOfficalMixin, UpdateView):
    model = Volunteer
    template_name = "update_racer.html"
    
    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Volunteer updated.')    
        return HttpResponseRedirect(self.get_success_url())
        
    def get_success_url(self):
        return "/volunteers/"