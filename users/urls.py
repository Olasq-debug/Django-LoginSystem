from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name = 'home'),
    path('register/', views.Register, name = 'register'),
    path('login/', views.UserLogin, name = 'login'),
    path('about/', views.about, name = 'about'),
    path('logout/', views.UserLogout, name = 'logout'),
    path('activate/<uid64>/<token>', views.Activate, name = 'activate'),
]