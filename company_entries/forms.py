from django import forms
from .models import CompanyEntry

class CompanyEntryForm(forms.Form):
    company_entry = forms.ModelChoiceField(queryset=CompanyEntry.objects.all())
