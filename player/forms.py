from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from city_engine.models import City


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Wprowadź swój adres mailowy')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CityCreationForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ('name',)