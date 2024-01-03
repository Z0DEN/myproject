import jwt
import requests
import json
import secrets
from django.core.cache import cache
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import CreateView

from MainApp.models import CloudUser, NodeModel

from .forms import CloudUserAuthForm, RegisterForm 
from .node import SendData
from .tokens import *


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===

global status_list

# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def CheckUsername(request):
    username = request.GET.get('username')
    if username == '':
        return JsonResponse({'is_taken': False})
    result = CloudUser.objects.filter(username=username).exists()
    return JsonResponse({'is_taken': result})
  

def GetToken(user):
    secret_key = secrets.token_hex(32)
    scopes = ["read", "write"]
    issued_at = datetime.utcnow()
    access_expiration = issued_at + timedelta(minutes=100)
    refresh_expiration = issued_at + timedelta(hours=1)
    user_model = CloudUser.objects.get(username=user.username)

    refresh_payload = {
        "sub": user.username,
        "exp": refresh_expiration,
        "iat": issued_at,
        "scopes": scopes,
    }

    access_payload = {
        "sub": user.username,
        "exp": access_expiration,
        "iat": issued_at,
        "scopes": scopes,
    }

    access_token = generate_token(access_payload, secret_key)
    refresh_token = generate_token(refresh_payload, secret_key)

    user.user_access_token=access_token
    user.user_refresh_token=refresh_token
    user.secret_key=secret_key
    user.save()
    return access_token, refresh_token


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def Registration(request):
   if request.method != "POST":
       form = RegisterForm()
       return render(request, "registration/registration.html", {"form": form})
   else:
       form = RegisterForm(request.POST)
       if not form.is_valid():
           return render(request, "registration/registration.html", {"form": form})
       else:
           form.save()
           username = form.cleaned_data["username"]
           password = form.cleaned_data["password1"]

           user = authenticate(request, username=username, password=password)

           if user is not None:
               node = NodeModel.objects.order_by('user_quantity').first()
               node_domain = node.node_domain
               node.user_quantity += 1
               node.save()

               user.node_domain = node_domain
               user.save()
               login(request, user)

               data_to_send = {
                  'username': user.username,
                  'node_UUID': node.UUID,
                  'func': 'AddUser',
               }
               SendData(data_to_send)
               access_token, refresh_token = GetToken(user)
               response = HttpResponseRedirect(reverse('MainApp:profile'))
               response.set_cookie('access_token', access_token, httponly=True)
               response.set_cookie('refresh_token', refresh_token, httponly=True)
               return response


def UserLogin(request):
    if request.method != 'POST':
        return render(request, 'registration/login.html')
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        access_token, refresh_token = GetToken(user)
        response = HttpResponseRedirect(reverse('MainApp:profile'))
        response.set_cookie('access_token', access_token, httponly=True)
        response.set_cookie('refresh_token', refresh_token, httponly=True)
        return response


@login_required
def UserLogout(request):
    logout(request)
    response = HttpResponseRedirect(reverse('MainApp:profile'))
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
    #return redirect("MainApp:profile")


def UserTokenUpdate(data):
    print('user token update')

# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


@csrf_protect
def HomeRender(request):
    return render(request, "main/home.html")


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


@login_required
def ProfileRender(request):
    MY_VARIABLES = settings.MY_VARIABLES
    context = MY_VARIABLES
    return render(request, "registration/profile.html", context)


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


# ------------------------------------------------------------- #
#                            STATUSES                           #
# ------------------------------------------------------------- #
#   1<..>  -> Error
#   2<..>  -> Success
#   3<..>  -> Warning
#   4<..>  -> Info

status_list = {
    10: "Undefined error. ",
    11: "Node already exists. ",
    12: "Invalid request method. ",
    13: "Invalid request data. ",
    14: "Token is expired. ",
    15: "Invalid Token. ",
    16: "Request have no auth token (Bearer). ",
    17: "Node with the following details already exists. ",
    # ------------------------------------------------------------- #
    20: "Undefined success. ",
    21: "Node or user was successfully created. ",
    22: "Token is Valid. ",
    23: "Data successfully changed. ",
    # ------------------------------------------------------------- #
    30: "Undefined warning. ",
    # ------------------------------------------------------------- #
    40: "Undefined info. ",
}
