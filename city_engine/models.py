from django.db import models
from django.conf import settings


class City(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.TextField(max_length=15, unique=True)
    publish = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
