import datetime
import json
import secrets
from datetime import datetime, timedelta

import jwt
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
            AddUser(user)
            return redirect("MainApp:profile")
        return response

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def AddUser(user):
        :

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
    def ChangeData(node_domain, IN_IP, EX_IP, UUID):
        node = NodeModel.objects.get(UUID=UUID)
        node.node_domain = node_domain
        node.IN_IP = IN_IP
        node.EX_IP = EX_IP
        node.save()

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def IsNodeExist(node_domain, IN_IP, EX_IP):
        arg_dict = {"node_domain": node_domain, "IN_IP": IN_IP, "EX_IP": EX_IP}
        ResponseText = "Узел с данными параметрами уже существует: "
        var = 0
        existing_values = []
        for arg_key, arg_value in arg_dict.items():
            if NodeModel.objects.filter(**{arg_key: arg_value}).exists():
                arg_string = f"{arg_key}: {arg_value}"
                existing_values.append(str(arg_string))
                var += 1
        if var != 0:
            ResponseText += ", ".join(existing_values)
            return ResponseText, True
        return ResponseText, False

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def CreateNewNode(node_domain, IN_IP, EX_IP, UUID):
        if NodeModel.objects.filter(UUID=UUID).exists():
            if NodeModel.objects.filter(
                node_domain=node_domain, IN_IP=IN_IP, EX_IP=EX_IP
            ):
                return "Данный узел уже существует.", 400
            ChangeData(node_domain, IN_IP, EX_IP, UUID)
            return "Данные узла обновлены.", 200

        ResponseText, success = IsNodeExist(node_domain, IN_IP, EX_IP)

        if success:
            return ResponseText, 400

        new_node = NodeModel(
            node_domain=node_domain,
            IN_IP=IN_IP,
            EX_IP=EX_IP,
            UUID=UUID,
            user_quantity=0,
        )
        new_node.save()
        return "Узел успешно создан.", 200

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    if request.method != "POST":
        return HttpResponse("Invalid request method.", status=405)

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    data = json.loads(request.body)

    node_domain = data.get("node_domain")
    IN_IP = data.get("IN_IP")
    EX_IP = data.get("EX_IP")
    UUID = data.get("UUID")

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    if node_domain is None or IN_IP is None or EX_IP is None or UUID is None:
        return HttpResponse("Недостаточно данных для создания узла.", status=400)

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    Response, status = CreateNewNode(node_domain, IN_IP, EX_IP, UUID)
    return HttpResponse(Response, status=status)


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def generate_token(payload, secret_key):
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def decode_token(token, secret_key):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        return "Token is Valid", 0
    except jwt.ExpiredSignatureError:
        return "Token is expired", 1
    except jwt.InvalidTokenError:
        return "Invalid Token", 2


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

    token = UserToken.objects.create(user=user_model, access_token=access_token, refresh_token=refresh_token, secret_key=secret_key)

    json_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return JsonResponse(json_data, safe=False)


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


def update_token(user, new_token):
    user.token = generate_token()
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
