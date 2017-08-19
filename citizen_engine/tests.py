from django.test import TestCase
from .models import Citizen
from city_engine.models import City
# Create your functional_tests here.


class NewCitizenTest(TestCase):

    def setUp(self):
        city = City.objects.create(name='Wrocław')
        global city
        citizen = Citizen.objects.create(name='Jan', surname='Strumecki', age=40, health=25, city=city)

    def test_if_citizen_exist(self):
        self.assertTrue(Citizen.objects.filter(name='Jan',
                                               surname='Strumecki',
                                               age=40,
                                               health=25,
                                               city=city.id))
    # def test_if_validation