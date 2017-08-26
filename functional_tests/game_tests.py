from selenium import webdriver
from city_engine.models import City
from selenium.webdriver.common.keys import Keys
import unittest


class TurnSystemTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()
        City.objects.create(name='Wrocław')

    def test_if_turn_work_correct(self):
        city = City.objects.get(name='Wrocław')
        self.browser.get('http://localhost:8000/{}/main_view'.format(city.id))
        self.assertIn('Miasto {}'.format(city.name), self.browser.title)
        button = self.browser.find_element('button')
        for x in range(12):
            button.send_keys(Keys.ENTER)