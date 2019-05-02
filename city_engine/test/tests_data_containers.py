from django import test
from django.contrib.auth.models import User

from citizen_engine.models import Citizen, Profession, Education, Family
from city_engine.models import (
    City,
    WindPlant,
    DumpingGround,
    StandardLevelResidentialZone,
)
from cou.abstract import RootClass
from cou.global_var import COLLEGE, FEMALE, ELEMENTARY, PHD, MALE
from player.models import Profile
from resources.models import Market


class DataContainersTests(test.TestCase):
    fixtures = ["basic_fixture_resources_and_employees.json"]

    def setUp(self):
        self.city = City.objects.latest("id")
        self.user = User.objects.latest('id')
        Market.objects.create(profile=self.user.profile)

    def test_valid_field_for_building_with_worker(self):
        dg = DumpingGround.objects.latest("id")
        wp = WindPlant.objects.latest("id")
        RC = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(RC.list_of_buildings[dg].elementary_vacancies, 5)
        self.assertEqual(RC.list_of_buildings[dg].college_vacancies, 0)
        self.assertEqual(RC.list_of_buildings[dg].phd_vacancies, 0)

        self.assertEqual(RC.list_of_buildings[wp].elementary_vacancies, 5)
        self.assertEqual(RC.list_of_buildings[wp].college_vacancies, 0)
        self.assertEqual(RC.list_of_buildings[wp].phd_vacancies, 0)

    def test_salary_expectation_calculation_without_education(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        s = Citizen.objects.create(
            city=self.city,
            age=18,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            resident_object=sr,
        )
        Profession.objects.create(citizen=s, proficiency=0.5, name="Nauczyciel")
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(rc.citizens_in_city[s].salary_expectation, 0)

    def test_salary_expectation_calculation_without_profession(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        s = Citizen.objects.create(
            city=self.city,
            age=18,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=COLLEGE,
            resident_object=sr,
        )
        Education.objects.create(
            citizen=s, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=s, name=COLLEGE, effectiveness=1, if_current=False
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(rc.citizens_in_city[s].salary_expectation, 0)

    def test_salary_expectation_calculation_without_residential_object(self):
        s = Citizen.objects.create(
            city=self.city,
            age=18,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=COLLEGE,
        )
        Education.objects.create(
            citizen=s, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=s, name=COLLEGE, effectiveness=1, if_current=False
        )
        Profession.objects.create(citizen=s, proficiency=0.5, name="Nauczyciel")
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(rc.citizens_in_city[s].salary_expectation, 0)

    def test_valid_field_for_citizen_pass(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        s = Citizen.objects.create(
            city=self.city,
            age=18,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=COLLEGE,
            resident_object=sr,
        )
        Education.objects.create(
            citizen=s, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=s, name=COLLEGE, effectiveness=1, if_current=False
        )
        Profession.objects.create(citizen=s, proficiency=0.5, name="Nauczyciel")
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=ELEMENTARY,
            resident_object=sr,
        )
        Education.objects.create(
            citizen=m, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Profession.objects.create(citizen=m, proficiency=0.2, name="Spawacz")
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=PHD,
            resident_object=sr,
        )
        Education.objects.create(
            citizen=p, name=ELEMENTARY, effectiveness=1, if_current=False
        )
        Education.objects.create(
            citizen=p, name=COLLEGE, effectiveness=1, if_current=False
        )
        Education.objects.create(citizen=p, name=PHD, effectiveness=1, if_current=False)
        Profession.objects.create(
            citizen=p, proficiency=0.8, name="Nauczyciel Akademicki"
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(rc.citizens_in_city[s].salary_expectation, 242.4)
        self.assertEqual(
            rc.citizens_in_city[m].salary_expectation,
            96.9599999999999937472239253111183643341064453125,
        )
        self.assertEqual(
            rc.citizens_in_city[p].salary_expectation,
            436.31999999999999317878973670303821563720703125,
        )

    def test_family_data_container_one_family(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family = Family.objects.create(city=self.city)
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="2",
            sex=FEMALE,
            education=PHD,
            resident_object=sr,
            family=family,
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(rc.families), 1)
        self.assertEqual(rc.families[family].members, [p])

    def test_family_data_container_two_family(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family_p = Family.objects.create(city=self.city)
        family_m = Family.objects.create(city=self.city)
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=PHD,
            resident_object=sr,
            family=family_p,
        )
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="2",
            sex=MALE,
            education=ELEMENTARY,
            resident_object=sr,
            family=family_m,
        )
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(rc.families), 2)
        self.assertEqual(rc.families[family_p].members, [p])
        self.assertEqual(rc.families[family_m].members, [m])

    def test_family_data_container_one_family_with_two_persons(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family = Family.objects.create(city=self.city)
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=FEMALE,
            education=PHD,
            resident_object=sr,
            family=family,
        )
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="2",
            sex=MALE,
            education=ELEMENTARY,
            resident_object=sr,
            family=family,
        )
        p.partner_id = m.id
        m.partner_id = p.id
        p.save()
        m.save()
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(rc.families), 1)
        self.assertIn(p, rc.families[family].members)
        self.assertIn(m, rc.families[family].members)

    def test_for_parent_attr_witch_child(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family = Family.objects.create(city=self.city)
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=MALE,
            education=PHD,
            resident_object=sr,
            family=family,
        )
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="2",
            sex=FEMALE,
            education=ELEMENTARY,
            resident_object=sr,
            family=family,
        )
        d = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=6,
            cash=100,
            health=5,
            name="0",
            surname="3",
            sex=FEMALE,
            resident_object=sr,
            family=family,
            mother_id=m.id,
            father_id=p.id,
        )
        p.partner_id = m.id
        m.partner_id = p.id
        p.save()
        m.save()
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(len(rc.families), 1)
        self.assertIn(p, rc.families[family].members)
        self.assertIn(m, rc.families[family].members)
        self.assertIn(d, rc.families[family].members)
        self.assertIn(p, rc.families[family].parents)
        self.assertIn(m, rc.families[family].parents)

    def test_pay_rent_success(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family = Family.objects.create(city=self.city)
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=150,
            health=5,
            name="0",
            surname="1",
            sex=MALE,
            education=PHD,
            resident_object=sr,
            family=family,
        )
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=70,
            health=5,
            name="0",
            surname="2",
            sex=FEMALE,
            education=ELEMENTARY,
            resident_object=sr,
            family=family,
        )
        p.partner_id = m.id
        m.partner_id = p.id
        p.save()
        m.save()
        self.assertEqual(self.city.cash, 1000000.00)
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(rc.families[family].cash, 220)
        self.assertEqual(rc.citizens_in_city[p].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[m].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[p].instance.cash, 150)
        self.assertEqual(rc.citizens_in_city[m].instance.cash, 70)
        self.assertEqual(rc.list_of_buildings[sr].instance.cash, 0)
        rc.families[family].pay_rent(self.city, self.user.profile)
        self.assertEqual(rc.citizens_in_city[p].instance.cash, 109.00)
        self.assertEqual(rc.citizens_in_city[m].instance.cash, 29)
        self.assertEqual(float(rc.list_of_buildings[sr].instance.cash), 81.18)
        self.assertEqual(float(self.city.cash), 1000000.82)
        self.assertEqual(rc.citizens_in_city[p].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[m].instance.resident_object, sr)

    def test_pay_rent_eviction(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family = Family.objects.create(city=self.city)
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=20,
            health=5,
            name="0",
            surname="1",
            sex=MALE,
            education=PHD,
            resident_object=sr,
            family=family,
        )
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=20,
            health=5,
            name="0",
            surname="2",
            sex=FEMALE,
            education=ELEMENTARY,
            resident_object=sr,
            family=family,
        )
        p.partner_id = m.id
        m.partner_id = p.id
        p.save()
        m.save()
        self.assertEqual(self.city.cash, 1000000.00)
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(rc.families[family].cash, 40)
        self.assertEqual(rc.citizens_in_city[p].instance.cash, 20)
        self.assertEqual(rc.citizens_in_city[m].instance.cash, 20)
        self.assertEqual(rc.list_of_buildings[sr].instance.cash, 0)
        self.assertEqual(rc.citizens_in_city[p].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[m].instance.resident_object, sr)
        rc.families[family].pay_rent(self.city, self.user.profile)
        self.assertEqual(rc.families[family].cash, 40)
        self.assertEqual(rc.citizens_in_city[p].instance.cash, 20)
        self.assertEqual(rc.citizens_in_city[m].instance.cash, 20)
        self.assertEqual(rc.list_of_buildings[sr].instance.cash, 0)
        self.assertEqual(rc.citizens_in_city[p].instance.resident_object, None)
        self.assertEqual(rc.citizens_in_city[m].instance.resident_object, None)
        self.assertEqual(self.city.cash, 1000000.00)

    def test_pay_rent_failed_becouse_homless(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family = Family.objects.create(city=self.city)
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=1150,
            health=5,
            name="0",
            surname="1",
            sex=MALE,
            education=PHD,
            family=family,
        )
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=1170,
            health=5,
            name="0",
            surname="2",
            sex=FEMALE,
            education=ELEMENTARY,
            family=family,
        )
        p.partner_id = m.id
        m.partner_id = p.id
        p.save()
        m.save()
        self.assertEqual(self.city.cash, 1000000.00)
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(rc.families[family].cash, 2320)
        self.assertEqual(rc.citizens_in_city[p].instance.cash, 1150)
        self.assertEqual(rc.citizens_in_city[m].instance.cash, 1170)
        self.assertEqual(rc.list_of_buildings[sr].instance.cash, 0)
        self.assertEqual(rc.citizens_in_city[p].instance.resident_object, None)
        self.assertEqual(rc.citizens_in_city[m].instance.resident_object, None)
        rc.families[family].pay_rent(self.city, self.user.profile)
        self.assertEqual(rc.families[family].cash, 2320)
        self.assertEqual(rc.citizens_in_city[p].instance.cash, 1150)
        self.assertEqual(rc.citizens_in_city[m].instance.cash, 1170)
        self.assertEqual(rc.list_of_buildings[sr].instance.cash, 0)
        self.assertEqual(rc.citizens_in_city[p].instance.resident_object, None)
        self.assertEqual(rc.citizens_in_city[m].instance.resident_object, None)
        self.assertEqual(self.city.cash, 1000000)

    def test_pay_rent_success_but_without_18_years_old_son(self):
        sr = StandardLevelResidentialZone.objects.latest("id")
        family = Family.objects.create(city=self.city)
        son = Citizen.objects.create(
            city=self.city,
            age=6,
            month_of_birth=6,
            cash=150,
            health=5,
            name="0",
            surname="3",
            sex=MALE,
            resident_object=sr,
            family=family,
        )
        p = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=150,
            health=5,
            name="0",
            surname="1",
            sex=MALE,
            education=PHD,
            resident_object=sr,
            family=family,
        )
        m = Citizen.objects.create(
            city=self.city,
            age=28,
            month_of_birth=6,
            cash=70,
            health=5,
            name="0",
            surname="2",
            sex=FEMALE,
            education=ELEMENTARY,
            resident_object=sr,
            family=family,
        )
        p.partner_id = m.id
        m.partner_id = p.id
        p.save()
        m.save()
        self.assertEqual(self.city.cash, 1000000)
        rc = RootClass(self.city, User.objects.latest("id"))
        self.assertEqual(rc.families[family].cash, 370)
        self.assertEqual(rc.citizens_in_city[p].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[m].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[son].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[p].instance.cash, 150)
        self.assertEqual(rc.citizens_in_city[m].instance.cash, 70)
        self.assertEqual(rc.citizens_in_city[son].instance.cash, 150)
        self.assertEqual(rc.list_of_buildings[sr].instance.cash, 0)
        rc.families[family].pay_rent(self.city, self.user.profile)
        self.assertEqual(rc.citizens_in_city[p].instance.cash, 109)
        self.assertEqual(rc.citizens_in_city[m].instance.cash, 29)
        self.assertEqual(rc.citizens_in_city[son].instance.cash, 150)
        self.assertEqual(float(rc.list_of_buildings[sr].instance.cash), 81.18)
        self.assertEqual(float(self.city.cash), 1000000.82)
        self.assertEqual(rc.citizens_in_city[p].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[m].instance.resident_object, sr)
        self.assertEqual(rc.citizens_in_city[son].instance.resident_object, sr)
