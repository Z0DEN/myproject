from django.urls import path
from . import views
from . import node

app_name = 'MainApp'

urlpatterns = [
    path('', views.HomeRender, name="home"),
    path('profile/', views.ProfileRender, name="profile"),
    path('reg/', views.RegistrationView.as_view(), name='register'),
    path('logout/', views.UserLogout, name="logout"),
    path('login/', views.UserLogin, name="login"),
    path('NodeConnection/', node.NodeConnection),
    path('TokenVerify/', node.TokenVerify),
]

