from django.shortcuts import render
from .models import City


def main_view(request, city_id):
    return render(request, 'main_view.html', {'id': city_id})
