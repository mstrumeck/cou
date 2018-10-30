from django.db import models
from city_engine.models import WindPlant, WaterTower, ProductionBuilding, City, Residential, DumpingGround, DustCart, BuldingsWithWorkes
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from cou.global_var import TRAINEE, JUNIOR, MASTER, PROFESSIONAL, REGULAR,\
    MALE, FEMALE,\
    ELEMENTARY, COLLEGE, PHD


class Citizen(models.Model):
    EDUCATION = (
        (ELEMENTARY, 'Elementary'),
        (COLLEGE, 'College'),
        (PHD, 'PhD')
    )

    SEX = (
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )
    city = models.ForeignKey(City)
    name = models.CharField(max_length=15)
    surname = models.CharField(max_length=15)
    age = models.IntegerField()
    month_of_birth = models.IntegerField()
    sex = models.CharField(choices=SEX, max_length=5)
    edu_title = models.CharField(choices=EDUCATION, max_length=10, default='None')
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    health = models.IntegerField()

    partner_id = models.PositiveIntegerField(default=0)
    father_id = models.PositiveIntegerField(default=0)
    mother_id = models.PositiveIntegerField(default=0)

    workplace_content_type = models.ForeignKey(ContentType,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     related_name='workplace_place')
    workplace_object_id = models.PositiveIntegerField(null=True)
    workplace_object = GenericForeignKey('workplace_content_type', 'workplace_object_id')

    resident_content_type = models.ForeignKey(ContentType,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     related_name='resident_place')
    resident_object_id = models.PositiveIntegerField(null=True)
    resident_object = GenericForeignKey('resident_content_type', 'resident_object_id')

    school_content_type = models.ForeignKey(ContentType,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     related_name='school_place')
    school_object_id = models.PositiveIntegerField(null=True)
    school_object = GenericForeignKey('school_content_type', 'school_object_id')

    def find_work(self, workplaces, citizens, save_instance):
        matrix = {ELEMENTARY: 'elementary_vacancies', COLLEGE: 'college_vacancies', PHD: 'phd_vacancies', 'None': 'elementary_vacancies'}
        possible_workplaces = [w for w in workplaces if workplaces[w][matrix[self.edu_title]]]
        if possible_workplaces:
            best = self.find_best_work_option(possible_workplaces)
            self.workplace_object = best
            workplaces[best][matrix[self.edu_title]] += 1
            citizens[self]['current_profession'] = Profession.objects.create(
                citizen=self, name=best.profession_type_provided)
            save_instance.append(citizens[self]['current_profession'])

    def find_best_work_option(self, workplaces):
        col = self.resident_object.city_field.col
        row = self.resident_object.city_field.row
        pattern = sorted(workplaces, key=lambda x: (
            abs(x.city_field.col - col), abs(x.city_field.row - row)) if isinstance(x, BuldingsWithWorkes) else (0, 0))
        chances = {len(pattern)/x: y for x, y in enumerate(pattern, start=1)}
        return chances[sorted(chances.keys()).pop()]

    def __str__(self):
        return "{} {}".format(self.name, self.surname)


class Profession(models.Model):
    LEVELS = (
        (TRAINEE, "Trainee"),
        (JUNIOR, "Junior"),
        (REGULAR, "Regular"),
        (PROFESSIONAL, "Professional"),
        (MASTER, "Master")
    )
    levels_info = {level[0]: {'divisor': divisor, 'border': border} for level, divisor, border in zip(
        LEVELS, (50, 40, 190, 120, 480), (0.10, 0.40, 0.60, 1, 1.30)
    )}
    citizen = models.ForeignKey(Citizen)
    name = models.CharField(default='', max_length=15)
    level = models.CharField(choices=LEVELS, max_length=15, default=TRAINEE)
    cur_level = models.FloatField(default=0)
    if_current = models.BooleanField(default=True)

    def __level_divisor(self):
        return Profession.levels_info[self.level]['divisor']

    def __check_level(self):
        if self.cur_level > Profession.levels_info[self.level]['border']:
            cur_level_index = [level[0] for level in Profession.LEVELS].index(self.level)
            try:
                self.level = Profession.LEVELS[cur_level_index+1][0]
            except IndexError:
                self.level = Profession.LEVELS[-1][0]

    def update_level(self, citizens_in_city):
        citizen = citizens_in_city[self.citizen]
        citizen_education = [e.effectiveness for e in citizen['educations']]
        citizen['current_profession'].cur_level += (sum(citizen_education)/len(citizen_education))/self.__level_divisor()
        self.__check_level()


class Education(models.Model):
    EDUCATION = (
        (ELEMENTARY, 'Elementary'),
        (COLLEGE, 'College'),
        (PHD, 'PhD')
    )
    citizen = models.ForeignKey(Citizen)
    name = models.CharField(choices=EDUCATION, max_length=15)
    effectiveness = models.FloatField(default=0.00)
    if_current = models.BooleanField(default=True)
    cur_year_of_learning = models.PositiveIntegerField(default=0)
    max_year_of_learning = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
