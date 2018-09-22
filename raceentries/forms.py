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
    
class RaceEntryEnterForm(forms.ModelForm):
    radio_number = forms.ChoiceField()
    contact_info = forms.CharField()
    
    class Meta:
        model = RaceEntry
        fields = ('racer', 'race', 'starting_position', 'contact_info', 'radio_number')
        
    def __init__(self, *args, **kwargs):
        super(RaceEntryEnterForm, self).__init__(*args, **kwargs)
        current_race = RaceControl.shared_instance().current_race
        self.fields['race'].initial = current_race
        radio_numbers = range(8, 90)
        existing_numbers = Racer.objects.values_list('radio_number', flat=True)
        available_numbers = ["radio {}".format(str(x)) for x in radio_numbers]
        available_numbers = [x for x in available_numbers if x not in existing_numbers]
        available_numbers_tup = tuple([(element, element) for element in available_numbers])
        self.fields['radio_number'].choices = available_numbers_tup
        
        racers = Racer.objects.order_by().all()
        for racer in racers:
            racer.racer_number = int(racer.racer_number)
        racers = list(racers)
        racers.sort(key=lambda x: x.racer_number)
        racers_tup = tuple([racer.pk, "{} {}".format(racer.racer_number, racer.display_name)] for racer in racers)
        self.fields['racer'].choices = racers_tup