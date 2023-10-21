from django.contrib.auth.models import AbstractUser
from django.db import models

def add_new_node(node_domain, ip_address, user_quantity, date_added):
    new_node = NodeModel(
        node_domain=node_domain,
        ip_address=ip_address,
        user_quantity=user_quantity,
        date_added=date_added,
    )
    new_node.save()

# Добавление нового объекта в таблицу
add_new_node(
    node_domain='node1',
    ip_address='192.168.0.98',
    user_quantity='5',
    date_added='2006-01-31',
)

