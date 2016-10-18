from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import UpdateView
from nacccusers.models import NACCCUser
from django.contrib import messages
from nacccusers.auth import AuthorizedRaceOfficalMixin


class AuthorizedCheckpointsList(AuthorizedRaceOfficalMixin, ListView):
    template_name = "list_authorized_checkpoints.html"
    context_object_name = "users"
    model = NACCCUser

class UpdateAuthorizedCheckpoints(AuthorizedRaceOfficalMixin, UpdateView):
    fields = ['authorized_checkpoints']
    template_name = 'update_authorized_checkpoints.html'
    model = NACCCUser
    
    def get_success_url(self):
        messages.success(self.request, 'Authorized Checkpoints were updated')
        return '/authorizedcheckpoints/'