from django.db import models


class City(models.Model):
    name = models.TextField(max_length=15)
