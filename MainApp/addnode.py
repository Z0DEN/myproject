import requests
import json

host = "192.168.0.98"

node_domain = ""

ip_address = ""

url = f'http://{host}:8001/NodeConnection/'

data = {"node_domain": node_domain, "ip_address": ip_address}

response = requests.post(url, data=data)


if response.status_code == 500:
    print(response)
else:
    # The request failed or the JSON response is not valid
    print(response.status_code)

