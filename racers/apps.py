from django.apps import AppConfig

class RacersConfig(AppConfig):
    name = 'racers'
    verbose_name = "Racers"
    
    def ready(self):
        from paypal.standard.models import ST_PP_COMPLETED
        from paypal.standard.ipn.signals import valid_ipn_received
        from .views import show_me_the_money
        valid_ipn_received.connect(show_me_the_money)
        print 'connect __init__.py'
    