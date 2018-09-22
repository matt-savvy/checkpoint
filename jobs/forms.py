from django import forms
from .models import Job

SERVICE_REGULAR = 180
SERVICE_RUSH = 15
SERVICE_DOUBLE_RUSH = 7
    
SERVICE_CHOICES = (
    (SERVICE_REGULAR, 'Regular'),
    (SERVICE_RUSH, 'Rush'),
    (SERVICE_DOUBLE_RUSH, 'Double Rush'), 
)

class JobForm(forms.ModelForm):
    minutes_due_after_start = forms.ChoiceField(choices=SERVICE_CHOICES)
    
    class Meta:
        model = Job
        fields = ('job_id', 'race', 'pick_checkpoint', 'drop_checkpoint', 'points', 'minutes_ready_after_start', 'minutes_due_after_start', 'manifest')
