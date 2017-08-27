from selenium import webdriver
from city_engine.models import City
from django.contrib.auth.models import User
from selenium.webdriver.common.keys import Keys
import unittest


class TurnSystemTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        user = User.objects.create()
        City.objects.create(name='Wroclaw', user=user, cash=100)

    def tearDown(self):
        self.browser.quit()

    def test_if_turn_work_correct(self):
        city = City.objects.get(name='Wroclaw')
        self.browser.get('http://localhost:8000/{}/main_view'.format(city.id))
        # self.assertIn('Miasto {}'.format(city.name), self.browser.title)
        button = self.browser.find_element_by_tag_name('button')
