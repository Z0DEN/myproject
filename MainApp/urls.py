from django.urls import path
from . import views
from .views import RegistrationView

app_name = 'MainApp'

urlpatterns = [
    path('', views.home_render, name="home"),
    path('profile/', views.profile_render, name="profile"),
    path('register/', RegistrationView.as_view(template_name='registration.html'), name='register'),
]

