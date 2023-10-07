from django.contrib.auth.models import AbstractUser
from django.db import models

class CloudUser(AbstractUser):
    node_domain = models.CharField(max_length=20)
    username = models.CharField(max_length=150, unique=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='cloud_users',  # Add a related_name argument
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='cloud_users',  # Add a related_name argument
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
