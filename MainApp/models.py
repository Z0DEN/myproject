from django.contrib.auth.models import AbstractUser
from django.db import models


class CloudUser(AbstractUser):
    node_domain = models.CharField(max_length=20)
    user_access_token = models.CharField(max_length=256, default="user_access_token")
    user_refresh_token = models.CharField(max_length=256, default="user_refresh_token")
    available_space = models.BigIntegerField(default=16_106_127_360)


class NodeModel(models.Model):
    node_domain = models.CharField(max_length=20, unique=True)
    user_quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    IN_IP = models.CharField(max_length=15, unique=True)
    EX_IP = models.CharField(max_length=15, unique=True)
    UUID = models.CharField(max_length=32, unique=True)
    port = models.CharField(max_length=5, unique=True, default="False")
    node_available_space = models.BigIntegerField(default=144_955_146_240)
    node_access_token = models.CharField(max_length=256, default="node_access_token")
    node_refresh_token = models.CharField(max_length=256, default="node_refresh_token")
    secret_key = models.CharField(max_length=64, default="secret_key")


class ServerDataModel(models.Model):
    personal_key = models.CharField(max_length=64, default="personal_key")
