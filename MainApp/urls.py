from django.urls import path
from . import views
from .views import RegistrationView, LoginView

app_name = 'MainApp'

urlpatterns = [
    path('', views.home_render, name="home"),
    path('profile/', views.profile_render, name="profile"),
    path('reg/', RegistrationView.as_view(), name='register'),
    path('NodeConnection/', views.NodeConnection),
#    path('login/', LoginView.as_view(), name='login'),
]

