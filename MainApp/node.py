import requests
import json
import secrets
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from MainApp.models import NodeModel, ServerDataModel

from .tokens import *

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


def TokenVerify(request):
    print('token verify')


def UpdateNodeTokens(node):
    print('updating tokens')
    new_local_access_token, new_local_refresh_token, new_secret_key = get_token_for_node(node.UUID)
    
    if node.local_connection:
        url = f"http://{node.IN_IP}:8002/UpdateNodeTokens/"
    else:
        url = f"http://{node.EX_IP}:8002/UpdateNodeTokens/"

    headers = {
        'Authorization': 'server ' + node.node_refresh_token
    }
    data = {
        'UUID': node.UUID,
        'access_token': new_local_access_token,
        'refresh_token': new_local_refresh_token,
    }

    try:
        response = requests.post(url, data=data, headers=headers)
        response_data = response.json()
        status = response_data.get('status')
    except Exception as e:
        return 10

    if status != 23:
        return status

#    node.local_server_access_token = new_local_access_token
#    node.local_server_refresh_token = new_local_refresh_token
    node.secret_key = new_secret_key
    node.node_access_token = response_data.get('access_token')
    node.node_refresh_token = response_data.get('refresh_token')
    node.save()


def SendData(data):
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
    status = None

    try:
        response = requests.post(url, data=data, headers=headers)
        status = response.json().get('status')
    except Exception as e:
        pass

    if status != 21:
        status = UpdateNodeTokens(node)
        if status == 23:
            SendData(data)


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

        data["user_quantity"] = 0
        data["local_server_access_token"] = local_server_access_token
        data["local_server_refresh_token"] = local_server_refresh_token
        data["secret_key"] = secret_key

        new_node = NodeModel(**data)
        new_node.save()

        return local_server_access_token, local_server_refresh_token, 21

    # +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    if request.method != "POST":
        response_data["msg"] = STATUS_LIST[12]
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
        response_data["msg"] = STATUS_LIST[13]
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
        response_data["msg"] = STATUS_LIST[status]
    print(response_data)
    return JsonResponse(response_data)


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
    # ------------------------------------------------------------- #
    30: "Undefined warning. ",
    # ------------------------------------------------------------- #
    40: "Undefined info. ",
}
