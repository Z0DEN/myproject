from django.contrib.auth.models import AbstractUser
from django.db import models


class CloudUser(AbstractUser):
    node_domain = models.CharField(max_length=20)


class UserToken(models.Model):
    user = models.OneToOneField(CloudUser, on_delete=models.CASCADE)
    user_access_token = models.CharField(max_length=256)
    user_refresh_token = models.CharField(max_length=256)
    secret_key = models.CharField(max_length=64)


class NodeModel(models.Model):
    node_domain = models.CharField(max_length=20, unique=True)
    user_quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    IN_IP = models.CharField(max_length=15, unique=True)
    EX_IP = models.CharField(max_length=15, unique=True)
    UUID = models.CharField(max_length=32, unique=True)
    local_connection = models.CharField(max_length=5, default="False")
    local_server_access_token = models.CharField(max_length=256, default="123123123123123123")
    local_server_refresh_token = models.CharField(max_length=256, default="123123123123123123")
    node_access_token = models.CharField(max_length=256, default="123123123123123123")
    node_refresh_token = models.CharField(max_length=256, default="123123123123123123")
    secret_key = models.CharField(max_length=64, default="123123123123123123")
