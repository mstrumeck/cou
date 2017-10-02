from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class BaseTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()


