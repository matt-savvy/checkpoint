from django import forms
from .models import CompanyEntry
from racecontrol.models import RaceControl

class CompanyEntryForm(forms.Form):
    company_entry = forms.ModelChoiceField(queryset=CompanyEntry.objects.all())

    def __init__(self, *args, **kwargs):
        super(CompanyEntryForm, self).__init__(*args, **kwargs)
        rc = RaceControl.shared_instance()
        self.fields['company_entry'].queryset = CompanyEntry.objects.filter(race=rc.current_race).filter(entry_status=CompanyEntry.ENTRY_STATUS_RACING)
