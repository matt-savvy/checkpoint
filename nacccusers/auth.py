from django.shortcuts import redirect

class AuthorizedRaceOfficalMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('/mobilecheckpoint/')
        return super(AuthorizedRaceOfficalMixin, self).dispatch(request, *args, **kwargs)