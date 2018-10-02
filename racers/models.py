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
    
    HEAT_FIRST = 'a'
    HEAT_SECOND = 'b'
    HEAT_THIRD = 'c'
    HEAT_FOURTH = 'd'
    
    HEAT_CHOICE_OPTIONS = (
        (HEAT_FIRST, "10:00"),
        (HEAT_SECOND, "11:00"),
        (HEAT_THIRD, "12:00"),
        (HEAT_FOURTH, "13:00"),
    )
    
    RACER_CATEGORY_OPTIONS_SHORT = (
        (RACER_CATEGORY_MESSENGER, "Messenger"),
        (RACER_CATEGORY_NON_MESSENGER, "Non-Mess"),
        (RACER_CATEGORY_EX_MESSENGER, "Recovered")
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
    
    radio_numbers = range(8, 90)
    available_numbers = ["radio {}".format(str(x)) for x in radio_numbers]
    available_numbers_tup = tuple([(element, element) for element in available_numbers])
    
    
    """(Racer description)"""
    racer_number = models.CharField(max_length=3, unique=True, validators=[RegexValidator(r'^\d{1,10}$')])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nick_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_OPTIONS)
    category = models.IntegerField(choices=RACER_CATEGORY_OPTIONS)
    track = models.BooleanField("Racer is riding a brakeless track bike", default=False)
    cargo = models.BooleanField("Racer is doing the cargo race.", default=False)
    packet = models.BooleanField("Packet picked up.", default=False)
    heat = models.CharField(max_length=2, choices=HEAT_CHOICE_OPTIONS, default=HEAT_FIRST)
    shirt_size = models.CharField(max_length=2, choices=SHIRT_SIZE_OPTIONS, default=SHIRT_SIZE_MEDIUM)
    paid = models.BooleanField(default=False)
    paypal_tx = models.CharField(blank=True, max_length=100)
    team = models.CharField(blank=True, max_length=100)
    company = models.CharField(blank=True, max_length=100)
    radio_number = models.CharField(choices=available_numbers_tup, blank=True, max_length=100)
    contact_info = models.CharField(blank=True, max_length=100)
    
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
        
    @property
    def category_as_string_short(self):
        return self.RACER_CATEGORY_OPTIONS_SHORT[self.category][1]
    
    @property
    def heat_string(self):
        return dict(self.HEAT_CHOICE_OPTIONS)[self.heat]
    
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
    fixed_gear = models.BooleanField("riding a proper track bike?", default=False)
    packet_picked_up = models.BooleanField("packet is picked up?", default=False)
    radio = models.CharField(max_length=50, blank=True)
    
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