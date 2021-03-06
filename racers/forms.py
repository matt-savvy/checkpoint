from django import forms
from django.db import models
from .models import Racer, Volunteer

class RacerForm(forms.ModelForm):
    available_numbers = range(1, 1000)
    available_numbers_tup = tuple([(element, element) for element in available_numbers])
    racer_number = forms.ChoiceField(choices=available_numbers)
    class Meta:
        model = Racer

    def __init__(self, *args, **kwargs):
        super(RacerForm, self).__init__(*args, **kwargs)
        racer_numbers = range(500, 1000)
        existing_numbers = Racer.objects.values_list('racer_number', flat=True)
        numbers_to_fill = 300 - len(existing_numbers)
        for number in existing_numbers:
            number = int(number)
        existing_numbers = [int(x) for x in existing_numbers]
        available_numbers = [x for x in racer_numbers if x not in existing_numbers][:numbers_to_fill]
        available_numbers_tup = tuple([(element, str(element)) for element in available_numbers])
        self.fields['racer_number'].choices = available_numbers_tup
        if not kwargs['instance']:
            if 'heat' in self.fields:
                del self.fields['heat']
                        
class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer

class ShirtForm(forms.ModelForm):
    class Meta:
        model = Racer
        fields = ('shirt_size', 'nick_name')
        
class RegisterForm(forms.ModelForm):
    available_numbers = range(1, 1000)
    available_numbers_tup = tuple([(element, element) for element in available_numbers])
    racer_number = forms.ChoiceField(choices=available_numbers)
    
    class Meta:
        model = Racer
        fields = ('racer_number', 'first_name', 'last_name', 'nick_name', 'city', 'email', 'gender', 'category', 'team', 'company', 'shirt_size')
    
    def clean_nick_name(self):
            data = self.cleaned_data['nick_name']
            if data == self.cleaned_data['first_name'] or self.cleaned_data['last_name']:
                data = ""
            
            return data
    
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        racer_numbers = range(500, 1000)
        existing_numbers = Racer.objects.values_list('racer_number', flat=True)
        numbers_to_fill = 300 - len(existing_numbers)
        for number in existing_numbers:
            number = int(number)
        existing_numbers = [int(x) for x in existing_numbers]
        available_numbers = [x for x in racer_numbers if x not in existing_numbers][:numbers_to_fill]
        available_numbers_tup = tuple([(element, str(element)) for element in available_numbers])
        self.fields['racer_number'].choices = available_numbers_tup

class PickupForm(forms.ModelForm):
    class Meta:
        model = Racer
        fields = ('track', 'cargo')