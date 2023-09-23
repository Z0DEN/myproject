from django.urls import path
from . import views

app_name = 'MainApp'

urlpatterns = [
    path('', views.home_render, name="home"),
    path('profile/', views.profile_render, name="profile"),
]

