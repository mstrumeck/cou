from django.test import TestCase
from city_engine.models import City, TurnSystem, Residential
from django.contrib.auth.models import User
from citizen_engine.models import Citizen
from django.db.models import Sum
from django.urls import reverse, resolve
from django.http import HttpRequest
from .views import main_view


class CityViewTests(TestCase):
    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Wrocław', user=user, cash=100)
        turns = TurnSystem.objects.create(city_id=city.id)
        citizen1 = Citizen.objects.create(age=40, health=25, city=city)
        citizen2 = Citizen.objects.create(age=25, health=35, city=city)
        citizen3 = Citizen.objects.create(age=15, health=45, city=city)
        residential1 = Residential.objects.create(max_population=20, city_id=city.id)
        residential2 = Residential.objects.create(max_population=20, city_id=city.id)

    def test_city_view(self):
        city = City.objects.get(name='Wrocław')
        response = self.client.get('/{}/main_view/'.format(city.id))
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, city.name)
        self.assertContains(response, 'Pieniądze: {}'.format(city.cash))
        self.assertContains(response, 'Domy: {}'.format(Residential.objects.filter(city_id=city.id).count()))
        self.assertContains(response, 'Mieszkańcy: {}/{}'.format(
            Citizen.objects.filter(city_id=city.id).count(),
            Residential.objects.filter(city_id=city.id).aggregate(Sum('max_population'))['max_population__sum']))
        self.assertContains(response, 'Dochody: {}'.format(
            Citizen.objects.filter(city_id=city.id).aggregate(Sum('income'))['income__sum']))


class CityPerformanceTests(TestCase):
    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Wrocław', user=user, cash=100)
        citizens = [Citizen() for i in range(1000)]


class TurnSystemTests(TestCase):
    def setUp(self):
        user = User.objects.create()
        city = City.objects.create(name='Wrocław', user=user, cash=100)
        TurnSystem.objects.create(city=city)

    def test_turn_view(self):
        city = City.objects.get(name='Wrocław')
        turns = TurnSystem.objects.get(city_id=city.id)
        response = self.client.get('/{}/main_view/'.format(city.id))
        self.assertTemplateUsed(response, 'main_view.html')
        self.assertContains(response, '{}/{}'.format(turns.current_turn, turns.max_turn))
        self.assertContains(response, 'Kolejna tura')