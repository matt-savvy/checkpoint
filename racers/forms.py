from django import forms
from .models import Racer

class RacerForm(forms.ModelForm):
    class Meta:
        model = Racer