import requests, json
headers = {
    'Authorization': 'server Bearer ' + 'access_token'
}
data = {'username': 'username',}
url = f"http://192.168.0.81:8002/AddUser/"
print('start post')
response = requests.post(url, data=json.dumps(data), headers=headers)
print(response)
