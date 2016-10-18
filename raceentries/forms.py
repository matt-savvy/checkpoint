from django import forms
from races.models import Race

class AdvanceForm(forms.Form):
    ADVANCE_FROM_TIME   = 'time'
    ADVANCE_FROM_POINTS = 'points'
    
    ADVANCE_FROM_CHOICES = (
        (ADVANCE_FROM_TIME, 'Fastest Time'),
        (ADVANCE_FROM_POINTS, 'Highest Points')
    )
    
    race_id = forms.IntegerField()
    advance_from = forms.ModelChoiceField(queryset=Race.objects.all())
    advance_using = forms.ChoiceField(choices=ADVANCE_FROM_CHOICES)
    number_to_advance = forms.IntegerField()
    