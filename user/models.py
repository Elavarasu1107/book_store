from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.BigIntegerField()
    location = models.CharField(max_length=255)
    is_verified = models.IntegerField(default=0)


class UserLog(models.Model):
    method = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField(default=1)
