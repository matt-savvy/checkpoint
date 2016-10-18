from django.db import models
from django.conf import settings

class Racer(models.Model):
        
    GENDER_MALE                     = 'M'
    GENDER_FEMALE                   = 'F'
    
    GENDER_OPTIONS = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female")
    )
    
    RACER_CATEGORY_MESSENGER        = 0
    RACER_CATEGORY_NON_MESSENGER    = 1
    RACER_CATEGORY_EX_MESSENGER     = 2
    RACER_CATEGORY_ERIN_YOUNG       = 3
    
    RACER_CATEGORY_OPTIONS = (
        (RACER_CATEGORY_MESSENGER, "Messenger"),
        (RACER_CATEGORY_NON_MESSENGER, "Non-Messenger"),
        (RACER_CATEGORY_EX_MESSENGER, "Ex-Messenger"),
        (RACER_CATEGORY_ERIN_YOUNG, "Erin Young")
    )
    
    
    
    """(Racer description)"""
    racer_number = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nick_name = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_OPTIONS)
    category = models.IntegerField(choices=RACER_CATEGORY_OPTIONS)
    paid = models.BooleanField(default=False)
    team = models.CharField(blank=True, max_length=100)

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

