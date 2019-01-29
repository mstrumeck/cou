from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from city_engine.models import City


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class CityCreationForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ("name",)
