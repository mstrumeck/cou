from django.test import TestCase
from django.contrib.auth.models import User
from .views import main_page, signup
from django.urls import resolve
from city_engine.models import City
from .forms import SignUpForm
from django.core.urlresolvers import reverse
from django.test import Client
import unittest


class TestLogin(TestCase):

    def setUp(self):
        User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')

    def testLogin(self):
        login = self.client.login(username='test_username', password='12345')
        self.assertTrue(login)


class PlayerViewTest(TestCase):

    def test_home_view_status_code(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/main_page.html')

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/')
        self.assertEquals(view.func, main_page)


class SignupFormTest(TestCase):

    def setUp(self):
        self.response = self.client.get('/signup/')

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)

    def test_csrf(self):
        response = self.client.get('/signup/')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_valid_new_user_data(self):
        url = '/signup/'
        data = {
            'username': 'michal',
            'email': 'strumecki@wp.pl',
            'password1': 'strumecki123',
            'password2': 'strumecki123',
            'name': 'Wrocław'
        }
        response = self.client.post(url, data)
        self.assertTrue(User.objects.exists())
        self.assertTrue(City.objects.exists())

    def test_invalid_new_user_data(self):
        url = '/signup/'
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 200)

    def test_invalid_new_user_data_with_empty_fields(self):
        url = '/signup/'
        data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            'name': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertFalse(City.objects.exists())

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="password"', 2)

    def test_dobuled_city_name(self):
        url = '/signup/'
        user = User.objects.create_user(username='test_username', password='12345', email='random@wp.pl')
        City.objects.create(name='Wrocław', user=user, cash=100).save()
        data = {
            'username': 'michal',
            'email': 'strumecki@wp.pl',
            'password1': 'strumecki123',
            'password2': 'strumecki123',
            'name': 'Wrocław'
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(City.objects.all().count(),1)

    # def test_contains_form(self):
    #     form = self.response.context.get('form')
    #     self.assertIsInstance(form, SignUpForm)


class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = '/signup/'
        data = {
            'username': 'michal',
            'email': 'strumecki@wp.pl',
            'password1': 'strumecki123',
            'password2': 'strumecki123',
            'name': 'Wrocław'
        }
        self.response = self.client.post(url, data)
        self.home_url = '/main_view/'

    def test_redirection(self):
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = '/signup/'
        self.response = self.client.post(url, {})

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    # def test_form_errors(self):
    #     form = self.response.context.get('form')
    #     self.assertTrue(form.errors)

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())


class SignUpFormTest(TestCase):
    def test_form_has_fields(self):
        form = SignUpForm()
        expected = ['username','password1', 'password2',]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)