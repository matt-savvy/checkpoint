from django import forms
from .models import Job

SERVICE_REGULAR = 'regular'
SERVICE_RUSH = 'rush'
SERVICE_DOUBLE_RUSH = 'double_rush'
    
SERVICE_CHOICES = (
    (SERVICE_REGULAR, 'Regular'),
    (SERVICE_RUSH, 'Rush'),
    (SERVICE_DOUBLE_RUSH, 'Double Rush'), 
)

class JobForm(forms.ModelForm):
    service = forms.ChoiceField(choices=SERVICE_CHOICES)
    
    class Meta:
        model = Job
        fields = ('job_id', 'race', 'pick_checkpoint', 'drop_checkpoint', 'minutes_ready_after_start', 'service', 'manifest')
    
    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        try:
            initial = kwargs.get('instance')
            if initial.minutes_due_after_start == 180:
                initial_service = SERVICE_REGULAR
            elif initial.minutes_due_after_start == 15:
                initial_service = SERVICE_RUSH
            elif initial.minutes_due_after_start == 7:
                initial_service = SERVICE_DOUBLE_RUSH
            
            self.fields['service'].initial = initial_service
        except:
            pass
       