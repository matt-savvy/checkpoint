from django.db import models

class Race(models.Model):
    
    RACE_TYPE_PRELIMS = 1
    RACE_TYPE_FINALS = 2
    RACE_TYPE_DISPATCH = 3
    
    RACE_TYPE_CHOICES = (
        (RACE_TYPE_PRELIMS, 'Prelims'),
        (RACE_TYPE_FINALS, 'Finals'),
        (RACE_TYPE_DISPATCH, 'Dispatch')
    )
    
    """(Race description)"""
    race_name = models.CharField(max_length=100)
    race_type = models.IntegerField(choices=RACE_TYPE_CHOICES, default=RACE_TYPE_PRELIMS)
    time_limit = models.IntegerField(default=0)
    race_start_time = models.DateTimeField(blank=True, null=True)
    

    def __unicode__(self):
        return self.race_name
    
    def get_absolute_url(self):
        return "/races/details/" + str(self.id) + "/"
