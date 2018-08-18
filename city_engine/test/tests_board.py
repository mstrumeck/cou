from django import test
from city_engine.models import City, WindPlant, WaterTower, DumpingGround, SewageWorks
from .base import TestHelper
from city_engine.main_view_data.board import Board, HexDetail, Hex
from cou.abstract import RootClass
from django.contrib.auth.models import User


class HexTest(test.TestCase, TestHelper):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.user = User.objects.latest('id')
        self.RC = RootClass(self.city, self.user)

    def test_create_empty_hex(self):
        self.assertEqual(
            Hex(row=0, col=0).create(),
            "<div class='hexagon'id='00'><div class='hexagon-top'></div>"
            "<div class='hexagon-middle'><p>0,0</p></div><div class='hexagon-bottom'></div>"
            "</div>"
        )
        self.assertEqual(
            Hex(row=3, col=3).create(),
            "<div class='hexagon'id='33'><div class='hexagon-top'></div>"
            "<div class='hexagon-middle'><p>3,3</p></div><div class='hexagon-bottom'></div></div>"
        )

    def test_double_crete_in_hex(self):
        hex = Hex(row=0, col=0)
        hex.create()
        self.assertEqual(
            hex.hexagon,
            "<div class='hexagon'id='00'><div class='hexagon-top'></div>"
            "<div class='hexagon-middle'><p>0,0</p></div><div class='hexagon-bottom'></div>"
            "</div>"
        )
        hex.create()
        self.assertEqual(
            hex.hexagon,
            "<div class='hexagon'id='00'><div class='hexagon-top'></div>"
            "<div class='hexagon-middle'><p>0,0</p></div><div class='hexagon-bottom'></div>"
            "</div>"
        )

    def test_hex_detail_with_instance(self):
        sw = SewageWorks.objects.latest('id')
        wp = WindPlant.objects.latest('id')
        wtp = WaterTower.objects.latest('id')
        self.assertEqual(
            Hex(row=0, col=0, instance=sw).create(),
            "<div class='hexagon build'id='00'><div class='hexagon-top'></div>"
            "<div class='hexagon-middle'>Oczyszczalnia ścieków<p>0,0</p></div>"
            "<div class='hexagon-bottom'></div></div>"
        )
        self.assertEqual(
            Hex(row=1, col=1, instance=wp).create(),
            "<div class='hexagon build'id='11'><div class='hexagon-top'></div>"
            "<div class='hexagon-middle'>Elektrownia wiatrowa<p>1,1</p></div>"
            "<div class='hexagon-bottom'></div></div>"
        )
        self.assertEqual(
            Hex(row=2, col=2, instance=wtp).create(),
            "<div class='hexagon build'id='22'><div class='hexagon-top'></div>"
            "<div class='hexagon-middle'>Wieża ciśnień<p>2,2</p></div>"
            "<div class='hexagon-bottom'></div></div>"
        )


class HexDetailTests(test.TestCase):
    fixtures = ['basic_fixture_resources_and_employees2.json']

    def setUp(self):
        self.city = City.objects.latest('id')
        self.user = User.objects.latest('id')
        self.RC = RootClass(self.city, self.user)

    def test_sewageworks_hex_box_detail(self):
        sw = SewageWorks.objects.latest('id')
        self.assertEqual(
            HexDetail(self.city, self.RC).add_sewage_works_details(sw),
            "<p>Pompowana czysta woda: 0/0</p><p>Przepustowość : 1000</p>"
        )

    def test_trashcollector_hex_box_detail(self):
        dg = DumpingGround.objects.latest('id')
        self.assertEqual(
            HexDetail(self.city, self.RC).add_trashcollector_details(dg),
            "<p>Energia: 0/1</p><p>Wysypisko: 0/10000</p><p>Lista śmieciarek:</p><p>Śmieciarka: załoga 0/3</p>"
        )

    def test_electricity_hex_box_detail(self):
        wp = WindPlant.objects.latest('id')
        self.assertEqual(
            HexDetail(self.city, self.RC).add_electricity_details(wp),
            '<p name="detailEnergy">Produkowana energia: 0</p><p>Zalokowana energia: 0</p><p>Liczba reaktorów: 1/10</p><p>Śmieci: None</p>'
        )

    def test_waterplant_hex_box_detail(self):
        wtp = WaterTower.objects.latest('id')
        self.assertEqual(
            HexDetail(self.city, self.RC).add_waterworks_details(wtp),
            '<p name="detailWater">Pompowana surowa woda: 0</p><p>Surowa woda zalokowana: 0</p><p>Śmieci: None</p>'
        )