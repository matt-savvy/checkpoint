from django import forms
from races.models import Race
from racers.models import Racer
from raceentries.models import RaceEntry
from racecontrol.models import RaceControl

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
    
class CutForm(forms.Form):
    men_to_keep = forms.IntegerField()
    wtf_to_keep = forms.IntegerField()
    messengers_only = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(CutForm, self).__init__(*args, **kwargs)
        current_race = RaceControl.shared_instance().current_race
        men = RaceEntry.objects.filter(race=current_race).filter(racer__gender=Racer.GENDER_MALE).count()
        wtf = RaceEntry.objects.filter(race=current_race).exclude(racer__gender=Racer.GENDER_MALE).count()
        self.fields['men_to_keep'].initial = men
        self.fields['wtf_to_keep'].initial = wtf