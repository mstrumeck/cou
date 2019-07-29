from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from city_engine.models import City
from map_engine.models import Map


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class CityCreationForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ("name",)


class MapForm(forms.Form):
    maps = forms.ModelChoiceField(queryset=Map.objects.all(), widget=forms.RadioSelect)
