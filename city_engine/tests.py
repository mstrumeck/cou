from django.test import TestCase
from city_engine.models import City
from django.urls import reverse, resolve
from django.http import HttpRequest
from .views import main_view


class CityViewTest(TestCase):
    def setUp(self):
        city = City.objects.create(name='Wrocław')
        global city

    def test_city_view(self):
        response = self.client.get('/{}/main_view/'.format(city.id))
        self.assertTemplateUsed(response, 'main_view.html')