from django.contrib.auth.models import AbstractUser
from django.db import models

class CloudUser(AbstractUser):
    node_domain = models.CharField(max_length=20)


class NodeModel():
    node_domain = models.CharField(max_length=20, unique=True)
    user_quantity = models.CharField(max_length=10)
    date_added = models.DateTimeField(auto_now_add=True)
