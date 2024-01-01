from django.contrib.auth.models import AbstractUser
from django.db import models


class CloudUser(AbstractUser):
    node_domain = models.CharField(max_length=20)
    user_access_token = models.CharField(max_length=256, default='user_access_token')
    user_refresh_token = models.CharField(max_length=256, default='user_refresh_token')
    secret_key = models.CharField(max_length=64, default='secret_key')


class NodeModel(models.Model):
    node_domain = models.CharField(max_length=20, unique=True)
    user_quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    IN_IP = models.CharField(max_length=15, unique=True)
    EX_IP = models.CharField(max_length=15, unique=True)
    UUID = models.CharField(max_length=32, unique=True)
    local_connection = models.CharField(max_length=5, default="False")
    local_server_access_token = models.CharField(max_length=256, default="local_server_access_token")
    local_server_refresh_token = models.CharField(max_length=256, default="local_server_refresh_token")
    node_access_token = models.CharField(max_length=256, default="node_access_token")
    node_refresh_token = models.CharField(max_length=256, default="node_refresh_token")
    secret_key = models.CharField(max_length=64, default="secret_key")


class ServerDataModel(models.Model):
    personal_key = models.CharField(max_length=64, default="personal_key")
