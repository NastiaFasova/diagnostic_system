import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    age_group = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    birthday = models.DateField(default=datetime.date.today)


class Diagnose(models.Model):
    title = models.CharField(max_length=100, default="unknown")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagnoses')
    pdf_file = models.FileField(upload_to='diagnose_pdfs')
    created_at = models.DateTimeField(auto_now_add=True)
