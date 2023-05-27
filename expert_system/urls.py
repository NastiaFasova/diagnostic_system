from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


urlpatterns = [
    path('', views.MainForm, name='request-form'),
    path('diagnose', login_required(views.diagnose))
]