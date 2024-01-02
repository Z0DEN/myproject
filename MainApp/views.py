import jwt
import requests
import json
import secrets
from datetime import datetime, timedelta
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

from MainApp.models import CloudUser, NodeModel, ServerDataModel

from .forms import CloudUserAuthForm, CloudUserLoginForm

# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===

global status_list

# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===


def generate_token(payload, secret_key):
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def decode_token(token, secret_key):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded, 22
    except jwt.ExpiredSignatureError:
        return None, 14
    except jwt.InvalidTokenError:
        return None, 15


def get_token_for_node(UUID):
    secret_key = secrets.token_hex(32)
    issued_at = datetime.utcnow()
    access_expiration = issued_at + timedelta(minutes=100)
    refresh_expiration = issued_at + timedelta(days=7)
    
    refresh_payload = {
        "sub": UUID,
        "exp": refresh_expiration,
        "iat": issued_at,
    }
    
    access_payload = {
        "sub": UUID,
        "exp": access_expiration,
        "iat": issued_at,
    }
    
    access_token = generate_token(access_payload, secret_key)
    refresh_token = generate_token(refresh_payload, secret_key)
    
    return access_token, refresh_token, secret_key


def UpdateNodeTokens():
    print('updating tokens')


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
            node = NodeModel.objects.order_by('user_quantity').first()
            node_domain = node.node_domain
            node.user_quantity += 1
            node.save()

            user.node_domain = node_domain
            user.save()
            login(self.request, user)
            
            data_to_send = {
                'username': user.username,
                'node_UUID': node.UUID,
                'func': 'AddUser',
            }
            self.SendData(data_to_send)
            return redirect("MainApp:profile")
        return response

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
    
    def SendData(self, data):
        node_UUID = data.pop('node_UUID')
        func = data['func']
        node = NodeModel.objects.get(UUID=node_UUID)
        access_token = node.node_access_token
        refresh_token = node.node_refresh_token
        if node.local_connection:
            url = f"http://{node.IN_IP}:8002/{func}/"
        else:
            url = f"http://{node.EX_IP}:8002/{func}/"
        headers = {
            'Authorization': 'server ' + access_token
        }

        response = requests.post(url, data=data, headers=headers)
        status = response.json().get('status')
    
        if status != 21:
            headers['Authorization'] = 'server ' + refresh_token
            response = requests.post(url, data=data, headers=headers)
            status = response.json().get('status')
            UpdateNodeTokens()
            if status != 21:
                print('All tokens is expired')

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+


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

    def ChangeNodeData(data, token_type, token):
        if token_type == 'personal':
            obj = ServerDataModel.objects.first()
            local_personal_key = getattr(obj, 'personal_key')
            if token != local_personal_key:
                return None, None, 15

        else:
            obj = NodeModel.objects.get(UUID=data['UUID'])
            secret_key = getattr(obj, 'secret_key')
            _, status = decode_token(token, secret_key)
            if status != 22:
                return None, None, status

        local_server_access_token, local_server_refresh_token, secret_key = get_token_for_node(data['UUID'])
        data["local_server_access_token"] = local_server_access_token
        data["local_server_refresh_token"] = local_server_refresh_token
        data["secret_key"] = secret_key
        NodeModel.objects.filter(UUID=data['UUID']).update(**data)
        return local_server_access_token, local_server_refresh_token, 23

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def IsNodeExist(data):
        ResponseText = "Node with the following details already exists: "
        var = 0
        existing_values = []
        for key, value in data.items():
            if (
                key != "local_connection" 
                and key != "node_access_token"
                and key != "node_refresh_token"
                and NodeModel.objects.filter(**{key: value}).exists()
            ):
                arg_string = f"{key}: {value}"
                existing_values.append(str(arg_string))
                var += 1
        if var != 0:
            ResponseText += ", ".join(existing_values)
            response_data["msg"] = ResponseText
            return True
        return False

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    def CreateNewNode(data, token_type, token):
        obj = NodeModel.objects.filter(UUID=data["UUID"])
        if obj.exists():
            new_local_access_token, new_local_refresh_token, status = ChangeNodeData(data, token_type, token)
            print('we get new local tokens')
            return new_local_access_token, new_local_refresh_token, status
        else:
            status = IsNodeExist(data)
            if status:
                return None, None, 17

        obj = ServerDataModel.objects.first()
        local_personal_key = getattr(obj, 'personal_key')
        if token != local_personal_key:
            return None, None, 15

        local_server_access_token, local_server_refresh_token, secret_key = get_token_for_node(data['UUID'])
        print('gettin new data')

        data["user_quantity"] = 0
        data["local_server_access_token"] = local_server_access_token
        data["local_server_refresh_token"] = local_server_refresh_token
        data["secret_key"] = secret_key

        new_node = NodeModel(**data)
        new_node.save()

        return local_server_access_token, local_server_refresh_token, 21

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
    node_server_access_token = data["node_access_token"]
    node_server_refresh_token = data["node_refresh_token"]
    bearer_header = request.headers.get('Authorization')
    token_type = bearer_header.split(' ')[0]
    bearer_token = bearer_header.split(' ')[1]
    print(token_type, '  ', bearer_token)
    print('data', data)

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    if (
        node_domain is None
        or IN_IP is None
        or EX_IP is None
        or UUID is None
        or local_connection is None
        or node_server_access_token is None
        or node_server_refresh_token is None
        or bearer_token is None
    ):
        response_data["msg"] = status_list[13]
        response_data["status"] = 13
        return JsonResponse(response_data)
    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    response_access_token, response_refresh_token, status = CreateNewNode(data, token_type, bearer_token)

    response_data = {
        "msg": response_data["msg"],
        "status": status,
        "access_token": response_access_token,
        "refresh_token": response_refresh_token,
    }
    if status != 17:
        response_data["msg"] = status_list[status]
    return JsonResponse(response_data)


# ++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++====++===



@login_required
def GetToken(request):
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

    user_model.user_access_token=access_token
    user_model.user_refresh_token=refresh_token
    user_model.secret_key=secret_key
    user_model.save()

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
    secret_key = "c96270ac89f1b1280792267ba7f63ae625c2040beeebd56ec6e48e638275c435"
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

# class NodeModel(models.Model):
#    node_domain = models.CharField(max_length=20, unique=True)
#    IN_IP = models.CharField(max_length=15, unique=True)
#    EX_IP = models.CharField(max_length=15, unique=True)
#    UUID = models.CharField(max_length=32, unique=True)
#    node_access_token = models.CharField(max_length=256, default="123123123123123123")
#    node_refresh_token = models.CharField(max_length=256, default="123123123123123123")
#    local_connection = models.CharField(max_length=5, default="False")

#    local_server_access_token = models.CharField(max_length=256, default="123123123123123123")
#    local_server_refresh_token = models.CharField(max_length=256, default="123123123123123123")
#    secret_key = models.CharField(max_length=64, default="123123123123123123")

#    user_quantity = models.IntegerField()

#    node_domain = data["node_domain"]
#    IN_IP = data["IN_IP"]
#    EX_IP = data["EX_IP"]
#    UUID = data["UUID"]
#    local_connection = data["local_connection"]
#    node_server_access_token = data["node_access_token"]
#    node_server_refresh_token = data["node_refresh_token"]
#
#    refresh_token ...in headers...
