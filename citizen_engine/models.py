from django.db import models
from city_engine.models import WindPlant, WaterTower, ProductionBuilding, City, Residential, DumpingGround, DustCart, BuldingsWithWorkes
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Citizen(models.Model):
    MALE = 'Ml'
    FEMALE = 'Fl'
    NONE = 'None'
    ELEMENTARY = 'EL'
    COLLEGE = 'COL'
    BACHELOR = 'BCH'

    SEX = (
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    EDUCATION = (
        (NONE, 'None'),
        (ELEMENTARY, 'Elementary'),
        (COLLEGE, 'College'),
        (BACHELOR, 'Bachelor')
    )
    city = models.ForeignKey(City)
    name = models.CharField(max_length=15)
    surname = models.CharField(max_length=15)
    age = models.IntegerField()
    month_of_birth = models.IntegerField()
    sex = models.CharField(choices=SEX, max_length=5)
    education = models.CharField(choices=EDUCATION, max_length=10)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    health = models.IntegerField()

    cur_year_of_learning = models.PositiveIntegerField(default=0)
    max_year_of_learning = models.PositiveIntegerField(default=0)

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

    def __str__(self):
        return "{} {}".format(self.name, self.surname)