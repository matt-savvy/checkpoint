from django.db import models
from django.contrib.auth.models import AbstractUser
from checkpoints.models import Checkpoint
#from dispatch.models import Dispatcher

class NACCCUser(AbstractUser):
    authorized_checkpoints = models.ManyToManyField(Checkpoint, blank=True)
    #authorized_dispatch = models.ManyToManyField(Dispatcher, blank=True)