from django.contrib.auth.models import AbstractUser
from django.db import models

class CloudUser(AbstractUser):
    node_domain = models.CharField(max_length=20)


class NodeModel(models.Model):
    node_domain = models.CharField(max_length=20, unique=True)
    ip_address = models.CharField(max_length=12, unique=True)
    user_quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.node_domain
