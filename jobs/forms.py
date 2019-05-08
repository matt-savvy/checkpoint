from django import forms
from .models import Job

SERVICE_SAMEDAY = 'sameday'
SERVICE_REGULAR = 'regular'
SERVICE_RUSH = 'rush'
SERVICE_DOUBLE_RUSH = 'double_rush'

SERVICE_CHOICES = (
    (None, '------'),
    (SERVICE_SAMEDAY, 'Same Day'),
    (SERVICE_REGULAR, 'Regular'),
    (SERVICE_RUSH, 'Rush'),
    (SERVICE_DOUBLE_RUSH, 'Double Rush'),
)

class JobForm(forms.ModelForm):
    service = forms.ChoiceField(choices=SERVICE_CHOICES)

    class Meta:
        model = Job
        fields = ('job_id', 'race', 'pick_checkpoint', 'drop_checkpoint', 'special_instructions', 'minutes_ready_after_start', 'service', 'service_label', 'minutes_due_after_start', 'points')

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        try:
            instance = kwargs.get('instance')
            service_label = instance.service_label.lower().replace(' ', "_")
            print service_label
            self.fields['service'].initial = service_label
        except:
            pass
