from django.contrib.auth.models import AbstractUser
from django.db import models


class CloudUser(AbstractUser):
    node_domain = models.CharField(max_length=20)


class UserToken(models.Model):
    user = models.OneToOneField(CloudUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    secret_key = models.CharField(max_length=64)


class NodeModel(models.Model):
    node_domain = models.CharField(max_length=20, unique=True)
    user_quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    IN_IP = models.CharField(max_length=15, unique=True)
    EX_IP = models.CharField(max_length=15, unique=True)
    UUID = models.CharField(max_length=32, default='00000000000000000000000000000000',unique=True)

    #    def __str__(self):
    #    return self.node_domain, self.EX_IP
