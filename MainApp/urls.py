from django.urls import path
from . import views
from . import node

app_name = 'MainApp'

urlpatterns = [
#    path('', views.HomeRender, name="home"),
    path('', views.ProfileRender, name="home"),
    path('reg/', views.Registration, name="register"),
    path('profile/', views.ProfileRender, name="profile"),
    path('logout/', views.UserLogout, name="logout"),
    path('login/', views.UserLogin, name="login"),
    path('CheckUsername/', views.CheckUsername),
    path('UserTokenUpdate/', views.UserTokenUpdate),
    path('NodeConnection/', node.NodeConnection),
    path('TokenVerify/', views.TokenVerify),
]

