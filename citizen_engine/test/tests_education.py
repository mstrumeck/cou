from django.contrib.auth.models import User
from django.test import TestCase
from city_engine.models import StandardLevelResidentialZone, City, WindPlant, CityField, PrimarySchool
from citizen_engine.models import Citizen, Education, Profession
from citizen_engine.citizen_creation import CreateCitizen
import random, string
from cou.abstract import RootClass
from citizen_engine.social_actions import SocialAction
from city_engine.turn_data.main import TurnCalculation
from player.models import Profile
from cou.global_var import FEMALE, ELEMENTARY, MALE, COLLEGE, TRAINEE, JUNIOR, REGULAR, MASTER, PROFESSIONAL


class TestEducation(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.profile = Profile.objects.latest('id')
        self.r1 = StandardLevelResidentialZone.objects.latest('id')
        self.f = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            education='None',
            resident_object=self.r1
        )
        self.school = PrimarySchool.objects.create(
            city=self.city,
            city_field=CityField.objects.latest('id')
        )
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.sa = SocialAction(self.city, self.profile, self.RC)

    def test_assign_student_to_school_pass_without_education(self):
        self.assertEqual(self.f.school_object, None)
        self.assertEqual(self.f.education_set.all().count(), 0)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.school.check_for_student_in_city(self.f,  RC.citizens_in_city[self.f])
        self.f.save()
        self.sa.update_age()
        e = Education.objects.get(citizen=self.f)
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.school_object, self.school)
        self.assertEqual(e.max_year_of_learning, self.school.years_of_education)
        self.assertEqual(self.f.education_set.all().count(), 1)
        self.assertEqual(e.if_current, True)

    def test_assign_student_to_school_pass_with_education(self):
        Education.objects.create(citizen=self.f, name=ELEMENTARY, effectiveness=0.5,
                                     cur_year_of_learning=4,
                                     max_year_of_learning=8,
                                     if_current=False)
        self.assertEqual(self.f.school_object, None)
        self.assertEqual(self.f.education_set.all().count(), 1)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.f].current_education, None)
        self.school.check_for_student_in_city(self.f, RC.citizens_in_city[self.f])
        TurnCalculation(self.city, RC, self.profile).save_all()
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(self.f.school_object, self.school)
        self.assertEqual(self.f.education_set.all().count(), 1)
        self.assertNotEqual(RC.citizens_in_city[self.f].current_education, None)
        self.assertEqual(RC.citizens_in_city[self.f].current_education.if_current, True)
        self.assertEqual(RC.citizens_in_city[self.f].current_education.max_year_of_learning,
                         self.school.years_of_education)

    def test_update_year_of_student_pass(self):
        Education.objects.create(cur_year_of_learning=0, max_year_of_learning=8, citizen=self.f, name=ELEMENTARY)
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.sa = SocialAction(self.city, self.profile, self.RC)
        self.assertEqual(self.RC.citizens_in_city[self.f].current_education.cur_year_of_learning, 0)
        self.school.update_year_of_school_for_student(self.f, self.RC.citizens_in_city[self.f].current_education)
        self.sa.update_age()
        self.RC.citizens_in_city[self.f].current_education.save()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(self.RC.citizens_in_city[self.f].current_education.cur_year_of_learning, 1)

    def test_gradudate_school_pass(self):
        self.f.school_object = self.school
        e = Education.objects.create(cur_year_of_learning=7, max_year_of_learning=8, citizen=self.f, name=ELEMENTARY)
        self.f.save()
        self.f = Citizen.objects.get(id=self.f.id)
        self.assertEqual(self.f.school_object, self.school)
        self.assertEqual(self.f.edu_title, "None")
        self.school.update_year_of_school_for_student(self.f, e)
        self.f.save()
        e.save()
        self.school.save()
        self.RC = RootClass(self.city, User.objects.latest('id'))
        self.sa = SocialAction(self.city, self.profile, self.RC)
        self.f = Citizen.objects.get(id=self.f.id)
        e = Education.objects.get(id=e.id)
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.f].current_education, None)
        self.assertEqual(e.cur_year_of_learning, 8)
        self.assertEqual(e.max_year_of_learning, 8)
        self.assertEqual(self.f.edu_title, ELEMENTARY)
        self.assertEqual(e.if_current, False)


class TestSchoolMonthlyRunFailed(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.profile = Profile.objects.latest('id')
        self.r1 = StandardLevelResidentialZone.objects.latest('id')
        self.school = PrimarySchool.objects.create(
            city=self.city,
            city_field=CityField.objects.latest('id')
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=MALE,
            education='None',
            resident_object=self.r1,
            school_object=self.school
        )
        self.s = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="2",
            sex=FEMALE,
            education=COLLEGE,
            resident_object=self.r1,
            workplace_object=self.school
        )

    # def test_gain_knowledge_without_profession_failed(self):
    #     Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
    #     Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
    #     Education.objects.create(citizen=self.m, name=ELEMENTARY)
    #     RC = RootClass(self.city, User.objects.latest('id'))
    #     self.assertEqual(RC.citizens_in_city[self.m]['current_education'].effectiveness, 0)
    #     self.assertEqual(RC.citizens_in_city[self.s]['current_profession'], None)
    #     self.school.monthly_run(RC.citizens_in_city, self.profile)
    #     self.assertEqual(RC.citizens_in_city[self.m]['current_education'].effectiveness, 0)
    #     self.assertEqual(RC.citizens_in_city[self.s]['current_profession'], None)

    def test_gain_knowledge_without_education_failed(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Profession.objects.create(citizen=self.s, proficiency=0.5, name='Nauczyciel')
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.m].current_education, None)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.5)
        self.school.monthly_run(RC.citizens_in_city, self.profile)
        self.assertEqual(RC.citizens_in_city[self.m].current_education, None)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.52)

    def test_gain_knowledge_without_teacher_education_failed_first_case(self):
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.m, name=ELEMENTARY)
        Profession.objects.create(citizen=self.s, proficiency=0.5, name='Nauczyciel')
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.m].current_education.effectiveness, 0)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.5)
        self.school.monthly_run(RC.citizens_in_city, self.profile)
        self.assertEqual(RC.citizens_in_city[self.m].current_education.effectiveness, 0)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.5)

    def test_gain_knowledge_without_teacher_education_failed_second_case(self):
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.m, name=ELEMENTARY)
        Profession.objects.create(citizen=self.s, proficiency=0.5, name='Nauczyciel')
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.m].current_education.effectiveness, 0)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.5)
        self.school.monthly_run(RC.citizens_in_city, self.profile)
        self.assertEqual(RC.citizens_in_city[self.m].current_education.effectiveness, 0)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.5)


class TestSchoolMonthlyRunPass(TestCase):
    fixtures = ['basic_fixture_resources_and_employees.json']

    def setUp(self):
        self.city = City.objects.get(id=1)
        self.profile = Profile.objects.latest('id')
        self.r1 = StandardLevelResidentialZone.objects.latest('id')
        self.school = PrimarySchool.objects.create(
            city=self.city,
            city_field=CityField.objects.latest('id')
        )
        self.m = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="0",
            surname="1",
            sex=MALE,
            education='None',
            resident_object=self.r1,
            school_object=self.school
        )
        self.s = Citizen.objects.create(
            city=self.city,
            age=8,
            month_of_birth=2,
            cash=100,
            health=5,
            name="AnonKA",
            surname="FeSurname",
            sex=FEMALE,
            education=COLLEGE,
            resident_object=self.r1,
            workplace_object=self.school
        )
        Education.objects.create(citizen=self.s, name=ELEMENTARY, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.s, name=COLLEGE, effectiveness=1, if_current=False)
        Education.objects.create(citizen=self.m, name=ELEMENTARY)
        Profession.objects.create(citizen=self.s, proficiency=0.5, name='Nauczyciel')

    def test_gain_knowledge_during_education_process_single_run(self):
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.m].current_education.effectiveness, 0.0)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.5)
        self.school.monthly_run(RC.citizens_in_city, self.profile)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.52)
        self.assertEqual(RC.citizens_in_city[self.m].current_education.effectiveness, 0.0052)

    def test_gain_knowledge_during_education_process_multi_run(self):
        RC = RootClass(self.city, User.objects.latest('id'))
        self.assertEqual(RC.citizens_in_city[self.m].current_education.effectiveness, 0.0)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.5)
        for x in range(6):
            self.school.monthly_run(RC.citizens_in_city, self.profile)
        self.assertEqual(RC.citizens_in_city[self.s].current_profession.proficiency, 0.5660526315789475)
        self.assertEqual(RC.citizens_in_city[self.m].current_education.effectiveness, 0.03360842105263158)