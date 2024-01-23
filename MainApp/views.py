import jwt
import requests
import json
import secrets
import redis
import time
from django_redis import get_redis_connection
from django.core.cache import cache
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import CreateView

from MainApp.models import CloudUser, NodeModel

from .forms import CloudUserAuthForm, RegisterForm, LoginForm
from .node import SendData
from .tokens import *


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===

global STATUS_LIST, REDISKA

REDISKA = redis.Redis(host='localhost', port=6379, password='redisisme', db=0)

# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def RJR(response_data={}, status=False, msg=False):
    response_data['status'] = status if status else "Success, or not success, that is the question"
    response_data['msg'] = STATUS_LIST[status] + msg if status and msg else STATUS_LIST[status] or msg if status or msg else "???UNDEFINED ERROR???"
    return JsonResponse(response_data)


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
    access_expiration = issued_at + timedelta(minutes=10)
    refresh_expiration = issued_at + timedelta(minutes=30)
    user_model = CloudUser.objects.get(username=user.username)

    refresh_payload = {
        "sub": user.username,
        "exp": int(refresh_expiration.timestamp()),
        "iat": int(issued_at.timestamp()),
        "scopes": scopes,
    }

    access_payload = {
        "sub": user.username,
        "exp": int(access_expiration.timestamp()),
        "iat": int(issued_at.timestamp()),
        "scopes": scopes,
    }

    access_token = generate_token(access_payload, secret_key)
    refresh_token = generate_token(refresh_payload, secret_key)

    REDISKA.setex(f"user_secret_key:{user.username}", 1800, secret_key)

    return access_token, refresh_token

@csrf_exempt
def TokenVerify(request):
    response_data = {
        'node_validate_status': None,
        'user_validate_status': None,
    }

    data = json.loads(request.body)
    bearer_header = request.headers.get('Authorization')
    node_bearer_token = bearer_header.split(' ')[1]
    node_UUID = data['node_UUID']
    node_secret_key = NodeModel.objects.get(UUID=node_UUID).secret_key
    _, validate_server_status = decode_token(node_bearer_token, node_secret_key)
    response_data['node_validate_status'] = validate_server_status
    if validate_server_status != 22:
        return RJR(response_data=response_data, status=22)

    user_token = data['Bearer']
    username = data['username']
    user_secret_key = REDISKA.get(f'user_secret_key:{username}')
    if user_secret_key is None:
        return RJR(response_data=response_data, status=22)

    _, validate_user_status = decode_token(user_token, user_secret_key) 
    response_data['user_validate_status'] = validate_user_status
    return RJR(response_data=response_data, status=22)


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
                     
                user.node_domain = node_domain
                user.save()
                login(request, user)

                num_users = CloudUser.objects.filter(node_domain=node_domain).count()
                node.user_quantity = num_users
                node.save()

                access_token, refresh_token = GetToken(user)
                response = HttpResponseRedirect(reverse('MainApp:profile'))
                response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=False)
                response.set_cookie('access_token', access_token, httponly=False, samesite='Lax', secure=False)

                data_to_send = {
                   'username': user.username,
                   'node_UUID': node.UUID,
                   'func': 'AddUser',
                }
                SendData(data_to_send)
                return response


def UserLogin(request):
    form = LoginForm(request.POST or None)
    context = {
       'STATUS': True,
       'form': form
    }
    if request.method == 'GET':
        return render(request, 'registration/login.html', context)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        access_token, refresh_token = GetToken(user)
        response = redirect('MainApp:profile')
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', secure=False)
        response.set_cookie('access_token', access_token, httponly=False, samesite='Lax', secure=False)
        return response
    else:
        context['STATUS'] = False
        context['ERROR'] = 'Invalid login or password'
        context['FORM_ERRORS'] = form.errors
    return render(request, 'registration/login.html', context)


@login_required
def UserLogout(request):
    REDISKA.delete(f'user_secret_key:{request.user}')
    logout(request)
    response = HttpResponseRedirect(reverse('MainApp:profile'))
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


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
    node_ip = NodeModel.objects.get(node_domain=request.user.node_domain).EX_IP
    context['NODE_IP'] = node_ip
    return render(request, "registration/profile.html", context)


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


# ------------------------------------------------------------- #
#                            STATUSES                           #
# ------------------------------------------------------------- #
#   1<..>  -> Error
#   2<..>  -> Success
#   3<..>  -> Warning
#   4<..>  -> Info

STATUS_LIST = {
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
    24: "User logged in successfully. ",
    # ------------------------------------------------------------- #
    30: "Undefined warning. ",
    # ------------------------------------------------------------- #
    40: "Undefined info. ",
}
