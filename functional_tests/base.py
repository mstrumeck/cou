from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from city_engine.models import City
from django.contrib.auth.models import User


class BaseTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

