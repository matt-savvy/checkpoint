from django.shortcuts import redirect
from django.utils import timezone
import pytz

class AuthorizedRaceOfficalMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('/mobilecheckpoint/')
        timezone.activate(pytz.timezone('US/Eastern'))
        return super(AuthorizedRaceOfficalMixin, self).dispatch(request, *args, **kwargs)
