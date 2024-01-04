from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import CloudUser


class CloudUserAuthForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CloudUser
        fields = ('username', 'password1', 'password2')
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }


class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CloudUser
        fields = ('username', 'password1', 'password2')


class LoginForm(forms.Form):
   username = forms.CharField(label='Username', max_length=100)
   password = forms.CharField(widget=forms.PasswordInput)

   def clean(self):
       username = self.cleaned_data.get('username')
       password = self.cleaned_data.get('password')

       if username and password:
           user = authenticate(username=username, password=password)
           if not user:
               raise forms.ValidationError("Пользователь не найден")
       return super().clean()
