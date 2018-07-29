from django.urls import resolve
from .base import CityFixture
from city_engine.views import resources_view
from cou.abstract import RootClass


class CityViewTests(CityFixture, RootClass):

    def test_call_view_loads(self):
        response = self.client.get('/main/resources/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources_view.html')

    def test_resources_url(self):
        view = resolve('/main/resources/')
        self.assertEquals(view.func, resources_view)
