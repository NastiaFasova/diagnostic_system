from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


urlpatterns = [
    path('image_upload', views.image_upload, name="image_upload"),
    path('analyze',  login_required(views.analyze)),
    path('upload', login_required(views.upload))
]