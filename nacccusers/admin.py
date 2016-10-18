from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import NACCCUser
from django import forms


class NACCCUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = NACCCUser


class NACCCUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = NACCCUser

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            NACCCUser.objects.get(username=username)
        except NACCCUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'], code='duplicate_username')


class NACCCUserAdmin(UserAdmin):
    form = NACCCUserChangeForm
    add_form = NACCCUserCreationForm

admin.site.register(NACCCUser, NACCCUserAdmin)