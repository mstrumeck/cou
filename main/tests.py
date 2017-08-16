from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
import unittest


class TestLogin(TestCase):
    def setUp(self):
        User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')

    def testLogin(self):
        login = self.client.login(username='test_username', password='12345')
        self.assertTrue(login)
