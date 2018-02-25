from django import forms
from .models import Racer

class RacerForm(forms.ModelForm):
    class Meta:
        model = Racer
        
class RegisterForm(forms.ModelForm):
    racer_number = forms.IntegerField(max_value=999, widget=forms.NumberInput)
    class Meta:
        model = Racer
        fields = ('racer_number', 'first_name', 'last_name', 'nick_name', 'city', 'email', 'gender', 'category', 'team', 'company')
        