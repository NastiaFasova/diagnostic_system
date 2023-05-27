from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


urlpatterns = [
    path('register', views.register, name='register'),
    path('login_user', views.login_user, name='login_user'),
    path('logout_user', views.logout_user, name='logout'),
    path('home', login_required(views.home)),
]