from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from map_engine.models import Map, Field

from city_engine.models import City


MAP_CHOICES = [(m.id, str(m.id)) for m in Map.objects.all() if Field.objects.filter(map=m, if_start=True)]


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class CityCreationForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ("name",)


class MapForm(forms.Form):
    maps = forms.ChoiceField(choices=MAP_CHOICES, widget=forms.RadioSelect)
