from django import forms
from races.models import Race

class ResultsForm(forms.Form):
    race = forms.ModelChoiceField(queryset=Race.objects.all())
    cut_line = forms.IntegerField(initial=0)
    cut_remark = forms.CharField(required=False, initial="Racers not in finals")
    show_dq = forms.BooleanField(required=False)
    show_dnf = forms.BooleanField(required=False)
    
    