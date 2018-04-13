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
from racers.models import Racer
from racers.forms import RacerForm, RegisterForm, ShirtForm
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
import hashlib
import pdb

class RacerListView(AuthorizedRaceOfficalMixin, ListView):
    model = Racer
    template_name = 'list_racers.html'
    context_object_name = 'racers'
    
    def get_context_data(self, **kwargs):
        context = super(RacerListView, self).get_context_data(**kwargs)
        #pdb.set_trace()
        queryset = context['object_list']
        context['total_men'] = len(queryset.filter(gender='M'))
        context['total_women'] = len(queryset.filter(gender='F'))
        context['total_trans'] = len(queryset.filter(gender='T'))
        
        context['total_mess'] = len(queryset.filter(category=0))
        context['total_non'] = len(queryset.filter(category=1))
        context['total_ex'] = len(queryset.filter(category=2))
        
        context['total_s'] = len(queryset.filter(shirt_size='S'))
        context['total_m'] = len(queryset.filter(shirt_size='M'))
        context['total_l'] = len(queryset.filter(shirt_size='L'))
        context['total_xl'] = len(queryset.filter(shirt_size='XL'))
        
        return context
    
    def get_queryset(self):
        return Racer.objects.all().order_by('racer_number')


class RacerListViewPublic(ListView):
    model = Racer
    template_name = 'list_racers_public.html'
    context_object_name = 'racers'
    
    def get_queryset(self):
        return Racer.objects.all().order_by('racer_number')


class RacerDetailView(AuthorizedRaceOfficalMixin, DetailView):
    template_name = 'racer_detail.html'
    model = Racer

class ThankYouView(TemplateView):
    template_name = 'thank_you.html'
    
    
def view_that_asks_for_money(request):
    try:
        racer_number = str(request.GET['racer_number'])
        url = request.build_absolute_uri(reverse('pay-view'))
        cancel_url = url + "?racer_number={}".format(racer_number)
    except:
        racer_number = ""
        cancel_url = request.build_absolute_uri(reverse('welcome-view'))
    
    item_name = "Registration for Racer {}".format(racer_number)    
    paypal_dict = {
        "business": "philabma@gmail.com",
        "amount": "50.00",
        "item_name": item_name,
       ## "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "notify_url": "http://2cdaf2eb.ngrok.io/paypal/",
        "return_url": request.build_absolute_uri(reverse('thank-you-view')),
        "cancel_return": cancel_url,
        ##custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, 'racer_pay.html', context)

@csrf_exempt
def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    print "show_me_the_money"
    print ipn_obj
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != "receiver_email@example.com":
            # Not a valid payment
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.
        
        ##if ipn_obj.mc_gross == price and ipn_obj.mc_currency == 'USD':
        ##    pass
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
          return context
    
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
        messages.success(self.request, 'Rider updated.')
        return reverse_lazy('thank-you-view')
    
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
