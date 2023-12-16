import datetime
import json
import secrets
from datetime import datetime, timedelta

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import CreateView

from MainApp.models import CloudUser, NodeModel, UserToken

from .forms import CloudUserAuthForm, CloudUserLoginForm

# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===

global status_list


class RegistrationView(CreateView):
    form_class = CloudUserAuthForm

    def get_template_names(self):
        return ["registration/registration.html"]

    success_url = reverse_lazy("MainApp:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            node = self.min_user_quantity_domain()
            node_domain = node.node_domain
            node.user_quantity += 1
            node.save()

            user.node_domain = node_domain
            user.save()
            login(self.request, user)
            self.AddUser(user)
            return redirect("MainApp:profile")
        return response

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def AddUser(self, user):
        user_node = user.node_domain
        node = NodeModel.objects.get(node_domain=user_node)
        if node.local_connection:
            url = f"https://{node.IN_IP}:8002/AddUser/"
        else:
            url = f"https://{node.EX_IP}:8002/AddUser/"

        data = {
            "username": user.username,
        }

        requests.post(url, data=data, verify=False)

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def min_user_quantity_domain(self):
        min_user_quantity = float("inf")
        min_user_quantity_node = None

        for node in NodeModel.objects.all():
            user_quantity = node.user_quantity
            if user_quantity < min_user_quantity:
                min_user_quantity = user_quantity
                min_user_quantity_node = node
        return min_user_quantity_node


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


class LoginView(View):
    form_class = CloudUserLoginForm
    template_name = "login.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("MainApp:home")
            else:
                form.add_error(None, "Invalid credentials")
        return render(request, self.template_name, {"form": form})


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


@csrf_exempt
def NodeConnection(request):
    global response_data
    response_data = {
        "msg": "",
        "status": 0,
        "access_token": "",
        "refresh_token": "",
    }

    def ChangeData(data):
        node = NodeModel.objects.get(UUID=UUID)
        for key, value in data.items():
            if key != "user_quantity" and key != "access_token" and key != "refresh_token":
                node.key = value
        node.save()
        accesss_token, refresh_token = node_token_update(data)
        return  accesss_token, refresh_token

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def IsNodeExist(data):
        print("подключение новой ноды, проверяем есть ли похожие данные у других узлов")
        ResponseText = "Node with the following details already exists: "
        var = 0
        existing_values = []
        print(data)
        for key, value in data.items():
            if (
                key != "local_connection"
                and NodeModel.objects.filter(**{key: value}).exists()
            ):
                print(key, ", ", value)
                print(NodeModel.objects.filter(**{key: value}).exists())
                arg_string = f"{key}: {value}"
                existing_values.append(str(arg_string))
                var += 1
                print(var)
        if var != 0:
            ResponseText += ", ".join(existing_values)
            response_data["msg"] = ResponseText
            return True
        return False

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def CreateNewNode(data):
        if NodeModel.objects.filter(UUID=data["UUID"]).exists():
            node_exists = NodeModel.objects.filter(**data).exists()
            if node_exists:
                return None, None, 11
            new_access_token, new_refresh_token = ChangeData(data)
            return new_access_token, new_refresh_token, 23
        else:
            status = IsNodeExist(data)
            print(status)
            if status:
                return None, None, 11

        secret_key = secrets.token_hex(32)
        issued_at = datetime.utcnow()
        access_expiration = issued_at + timedelta(minutes=100)
        refresh_expiration = issued_at + timedelta(hours=1)

        refresh_payload = {
            "sub": data["UUID"],
            "exp": refresh_expiration,
            "iat": issued_at,
        }

        access_payload = {
            "sub": data["UUID"],
            "exp": access_expiration,
            "iat": issued_at,
        }

        node_access_token = generate_token(access_payload, secret_key)
        node_refresh_token = generate_token(refresh_payload, secret_key)

        data["user_quantity"] = 0
        data["access_token"] = node_access_token
        data["refresh_token"] = node_refresh_token
        data["secret_key"] = secret_key

        new_node = NodeModel(**data)
        new_node.save()

        return node_access_token, node_refresh_token, 21

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    if request.method != "POST":
        response_data["msg"] = status_list[12]
        response_data["status"] = 12
        return JsonResponse(response_data)

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    data = json.loads(request.body)

    node_domain = data["node_domain"]
    IN_IP = data["IN_IP"]
    EX_IP = data["EX_IP"]
    UUID = data["UUID"]
    local_connection = data["local_connection"]

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    if (
        node_domain is None
        or IN_IP is None
        or EX_IP is None
        or UUID is None
        or local_connection is None
    ):
        response_data["msg"] = status_list[13]
        response_data["status"] = 13
        return JsonResponse(response_data)
    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    print(data)
    node_access_token, node_refresh_token, status = CreateNewNode(data)
    response_data = {
        "msg": status_list[status],
        "status": status,
        "access_token": node_access_token,
        "refresh_token": node_refresh_token,
    }
    return JsonResponse(response_data)


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def generate_token(payload, secret_key):
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def decode_token(token, secret_key):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded, 22
    except jwt.ExpiredSignatureError:
        return 14
    except jwt.InvalidTokenError:
        return 15


@login_required
def get_token(request):
    secret_key = secrets.token_hex(32)

    username = request.user.username
    scopes = ["read", "write"]
    issued_at = datetime.utcnow()
    access_expiration = issued_at + timedelta(minutes=100)
    refresh_expiration = issued_at + timedelta(hours=1)
    user_model = CloudUser.objects.get(username=username)

    refresh_payload = {
        "sub": username,
        "exp": refresh_expiration,
        "iat": issued_at,
        "scopes": scopes,
    }

    access_payload = {
        "sub": username,
        "exp": access_expiration,
        "iat": issued_at,
        "scopes": scopes,
    }

    access_token = generate_token(access_payload, secret_key)
    refresh_token = generate_token(refresh_payload, secret_key)

    token = UserToken.objects.create(
        user=user_model,
        access_token=access_token,
        refresh_token=refresh_token,
        secret_key=secret_key,
    )

    json_data = {
        "msg": status_list[20],
        "status": 20,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return JsonResponse(json_data)


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def token_verify(request):
    token = request.headers.get("Authorization")
    if token:
        token_type, token = token.split(" ")
        if token_type != "Bearer":
            return HttpResponse("Неверный тип токена")
    else:
        return HttpResponse("Токен не найден")
    # user = request.GET.user (запрос из другого сервера, поэтому через get будем передавать юзера, а вот на другом сервере получаем через request.user)
    # secret_key = "Будем получать из базы данных для данного пользователя"
    secret_key = "c96270ac89f1b1280792267ba7f63ae625c2040beeebd56ec6e48e638275c435"  # вообще-то secret_key нужно будет получать из базы данных по user из get запроса

    dec_access_token, status = decode_token(token, secret_key)
    if status == 1:
        return HttpResponse("Token is expired", status=status)
    elif status == 2:
        return HttpResponse("Invalid Token", status=status)

    json_data = {
        "dec_access_token": dec_access_token,
        "token": token,
    }
    json_response = json.dumps(json_data)
    return JsonResponse(json_response, safe=False)


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def node_token_update(data):
    new_secret_key = secrets.token_hex(32)
    issued_at = datetime.utcnow()
    access_expiration = issued_at + timedelta(minutes=100)
    refresh_expiration = issued_at + timedelta(hours=1)

    refresh_payload = {
        "sub": data["UUID"],
        "exp": refresh_expiration,
        "iat": issued_at,
    }

    access_payload = {
        "sub": data["UUID"],
        "exp": access_expiration,
        "iat": issued_at,
    }

    new_node_access_token = generate_token(access_payload, new_secret_key)
    new_node_refresh_token = generate_token(refresh_payload, new_secret_key)

    node = NodeModel.objects.get(UUID=data["UUID"])
    node.access_token = new_node_access_token
    node.refresh_token = new_node_refresh_token
    node.secret_key = new_secret_key
    node.save()
    return new_node_access_token, new_node_refresh_token


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def user_token_update(data):
    scopes = ["read", "write"]
    issued_at = datetime.utcnow()
    access_expiration = issued_at + timedelta(minutes=100)
    refresh_expiration = issued_at + timedelta(hours=1)

    refresh_payload = {
        "sub": data["username"],
        "exp": refresh_expiration,
        "iat": issued_at,
        "scopes": scopes,
    }

    access_payload = {
        "sub": data["username"],
        "exp": access_expiration,
        "iat": issued_at,
        "scopes": scopes,
    }
    new_secret_key = secrets.token_hex(32)
    new_access_token = generate_token(access_payload, new_secret_key)
    new_refresh_token = generate_token(refresh_payload, new_secret_key)
    user = CloudUser.objects.get(username=data["username"])
    user.access_token = new_access_token
    user.refresh_token = new_refresh_token
    user.secret_key = new_secret_key
    user.save()

# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


@csrf_protect
def home_render(request):
    return render(request, "main/home.html")


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


@login_required
def profile_render(request):
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
    10: "Undefined error",
    11: "Node already exists",
    12: "Invalid request method",
    13: "Invalid request data",
    14: "Token is expired",
    15: "Invalid Token",
    # ------------------------------------------------------------- #
    20: "Undefined success",
    21: "Node was successfully created",
    22: "Token is Valid",
    23: "Data successfully changed",
    # ------------------------------------------------------------- #
    30: "Undefined warning",
    # ------------------------------------------------------------- #
    40: "Undefined info",
}
