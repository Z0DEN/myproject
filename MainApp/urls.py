from . import views
from django.urls import path

urlpatterns = [
    path('', views.home_render, name="home"),
    path('profile', views.profile_render, name="profile"),
]
