from django import forms
from .models import Race
import pytz

class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = '__all__'

    def clean_race_start_time(self):
        start_time = self.cleaned_data['race_start_time']
        start_time = start_time.replace(tzinfo=pytz.timezone('US/Eastern'))
        return start_time
