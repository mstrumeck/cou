from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
from django.contrib.auth.models import User
from django.test import LiveServerTestCase


class NewPlayerSetupAccount(LiveServerTestCase):
    password = '12345'
    mail = 'michal.strumecki@wp.pl'
    nick = 'Kleju_0011'

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_create_new_account(self):
        self.browser.get('http://localhost:8081/signup')
        registration_form = self.browser.find_element_by_id('registration_form')

        nick_input = self.browser.find_element_by_id('nick')
        nick_input.send_keys(self.nick)

        mail_input = self.browser.find_element_by_id('e-mail_input')
        mail_input.send_keys(self.mail)

        password_input1 = self.browser.find_element_by_id('password')
        password_input1.send_keys(self.password)

        password_input2 = self.browser.find_element_by_id('password')
        password_input2.send_keys(self.password)

        registration_form.submit()

        users = User.objects.all()
        self.assertEqual(len(users), 1)

if __name__ == '__main__':
    unittest.main()



