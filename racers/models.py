from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

class Racer(models.Model):
    GENDER_MALE   = 'M'
    GENDER_FEMALE = 'F'
    GENDER_TRANS  = 'T'
    
    GENDER_OPTIONS = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_TRANS, "Trans/Non Binary/Agender")
    )
    
    RACER_CATEGORY_MESSENGER        = 0
    RACER_CATEGORY_NON_MESSENGER    = 1
    RACER_CATEGORY_EX_MESSENGER     = 2
    
    RACER_CATEGORY_OPTIONS = (
        (RACER_CATEGORY_MESSENGER, "Working Messenger"),
        (RACER_CATEGORY_NON_MESSENGER, "Non-Messenger"),
        (RACER_CATEGORY_EX_MESSENGER, "Recovered Messenger")
    )
    
    SHIRT_SIZE_SMALL  = 'S'
    SHIRT_SIZE_MEDIUM = 'M'
    SHIRT_SIZE_LARGE  = 'L'
    SHIRT_SIZE_XLARGE = 'XL'
    
    SHIRT_SIZE_OPTIONS = (
        (SHIRT_SIZE_SMALL, "S"),
        (SHIRT_SIZE_MEDIUM, "M"),
        (SHIRT_SIZE_LARGE, "L"),
        (SHIRT_SIZE_XLARGE, "XL")
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
    shirt_size = models.CharField(max_length=2, choices=SHIRT_SIZE_OPTIONS, default=SHIRT_SIZE_MEDIUM)
    paid = models.BooleanField(default=False)
    paypal_tx = models.CharField(blank=True, max_length=100)
    team = models.CharField(blank=True, max_length=100)
    company = models.CharField(blank=True, max_length=100)
    
    class Meta:
        ordering = ['last_name']
        
    def __unicode__(self):
        return self.display_name
        
    def get_absolute_url(self):
        return '/racers/details/' + str(self.id)
    
    @property
    def payment_link(self):
        return u'https://naccc.herokuapp.com/racers/pay/?racer_number={}'.format(str(self.racer_number))
    
    @property
    def shirt_link(self):
        return u'https://naccc.herokuapp.com/racers/shirt?pk={}&racer_number={}'.format(str(self.id), str(self.racer_number))

    @property
    def display_name(self):
        if len(self.nick_name) > 0:
            return u"{} '{}' {}".format(self.first_name, self.nick_name, self.last_name)
        return u"{} {}".format(self.first_name, self.last_name)
    
    @property
    def category_as_string(self):
        return self.RACER_CATEGORY_OPTIONS[self.category][1]
    
    def mark_as_paid(self):
        if not self.paid:
            self.paid = True
            self.save()
            
class Volunteer(models.Model):
    SHIRT_SIZE_SMALL  = 'S'
    SHIRT_SIZE_MEDIUM = 'M'
    SHIRT_SIZE_LARGE  = 'L'
    SHIRT_SIZE_XLARGE = 'XL'
    
    SHIRT_SIZE_OPTIONS = (
        (SHIRT_SIZE_SMALL, "S"),
        (SHIRT_SIZE_MEDIUM, "M"),
        (SHIRT_SIZE_LARGE, "L"),
        (SHIRT_SIZE_XLARGE, "XL")
    )
    
    """(Volunteer description)"""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, blank=True)
    phone = models.CharField("Phone Number", max_length=15)
    city = models.CharField(max_length=50, blank=True)
    shirt_size = models.CharField(max_length=2, choices=SHIRT_SIZE_OPTIONS, default=SHIRT_SIZE_MEDIUM)
    paid = models.BooleanField(default=False)
    paypal_tx = models.CharField(blank=True, max_length=100)
    
    class Meta:
        ordering = ['last_name']
        
    def __unicode__(self):
        return u"{} {}".format(self.first_name, self.last_name)
    
    def get_absolute_url(self):
        return '/volunteer/details/' + str(self.id)

    def mark_as_paid(self):
        if not self.paid:
            self.paid = True
            self.save()