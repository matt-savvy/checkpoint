from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
class Racer(models.Model):
        
    GENDER_MALE                     = 'M'
    GENDER_FEMALE                   = 'F'
    GENDER_TRANS                    = 'T'
    
    GENDER_OPTIONS = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_FEMALE, "Trans/Non Binary/Agender")
    )
    
    RACER_CATEGORY_MESSENGER        = 0
    RACER_CATEGORY_NON_MESSENGER    = 1
    RACER_CATEGORY_EX_MESSENGER     = 2
    
    RACER_CATEGORY_OPTIONS = (
        (RACER_CATEGORY_MESSENGER, "Working Messenger"),
        (RACER_CATEGORY_NON_MESSENGER, "Non-Messenger"),
        (RACER_CATEGORY_EX_MESSENGER, "Recovered Messenger")
    )
    
    """(Racer description)"""
    racer_number = models.CharField(max_length=3, unique=True, validators=[RegexValidator(r'^\d{1,10}$')])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nick_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_OPTIONS)
    category = models.IntegerField(choices=RACER_CATEGORY_OPTIONS)
    paid = models.BooleanField(default=False)
    team = models.CharField(blank=True, max_length=100)
    company = models.CharField(blank=True, max_length=100)

    def __unicode__(self):
        return self.display_name
        
    def get_absolute_url(self):
        return '/racers/details/' + str(self.id)

    @property
    def display_name(self):
        if len(self.nick_name) > 0:
            return u"{} '{}' {}".format(self.first_name, self.nick_name, self.last_name)
        return u"{} {}".format(self.first_name, self.last_name)
    
    @property
    def category_as_string(self):
        return self.RACER_CATEGORY_OPTIONS[self.category][1]

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from .views import show_me_the_money

valid_ipn_received.connect(show_me_the_money)
