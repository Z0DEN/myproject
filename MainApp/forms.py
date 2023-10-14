from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CloudUser


class CloudUserAuthForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CloudUser
        fields = ('username', 'password1', 'password2')


class CloudUserLoginForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CloudUser
        fields = ('username', 'password1')

