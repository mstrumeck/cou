from django.apps import apps
from city_engine.models import Building, CityField, BuldingsWithWorkes, Vehicle, PowerPlant, Waterworks, SewageWorks, Residential
from abc import ABCMeta
from django.db.models import Sum
from resources.models import Resource
from citizen_engine.models import Citizen, Education, Profession
from cou.global_var import ELEMENTARY, COLLEGE, PHD


class BasicAbstract(metaclass=ABCMeta):

    def get_subclasses(self, abstract_class, app_label):
        return [model for model in apps.get_app_config(app_label).get_models()
                if issubclass(model, abstract_class) and model is not abstract_class]

    def get_subclasses_of_all_buildings(self):
        return self.get_subclasses(abstract_class=Building, app_label='city_engine')

    def get_queries_of_vehicles(self):
        result = []
        for sub in self.get_subclasses(abstract_class=Vehicle, app_label='city_engine'):
            data = sub.objects.filter(city=self.city)
            if data.exists():
                for v in data:
                    result.append(v)
        return result

    def get_quersies_of_buildings(self):
        result = []
        for sub in self.get_subclasses_of_all_buildings():
            if sub.objects.filter(city=self.city).exists():
                data = sub.objects.filter(city=self.city)
                for b in data:
                    result.append(b)
        return result


class AbstractAdapter(BasicAbstract):
    pass


class ResourcesData(BasicAbstract):
    def __init__(self, city, user):
        self.city = city
        self.user = user
        self.subclasses_of_all_resources = self.get_subclasses(Resource, 'resources')
        self.resources = {ob.__name__: self.resources_size_and_sum(ob) for ob in [sub for sub in self.subclasses_of_all_resources]
                          if self.resources_size_and_sum(ob)[1]}

    def resources_size_and_sum(self, ob):
        data = ob.objects.filter(owner=self.user)
        return [data, data.values('size').aggregate(Sum('size'))['size__sum']]


class RootClass(BasicAbstract):
    def __init__(self, city, user):
        self.city = city
        self.user = user
        self.to_save = []
        self.city_fields_in_city = {}
        self.citizens_in_city = {}
        self.vehicles = {}
        self.list_of_buildings = {}
        self.preprocess_data()
        self.list_of_workplaces = {**{b: self.list_of_buildings[b] for b in self.list_of_buildings
                                      if isinstance(b, BuldingsWithWorkes)}, **self.vehicles}

    def preprocess_buildings(self, buildings, citizens):
        for b in buildings:
            self.to_save.append(b)
            self.list_of_buildings[b] = {
                'trash': [trash for trash in b.trash.all() if b.trash.all().exists()],
                'row_col_cor': (b.city_field.row, b.city_field.col),
                'people_in_charge': b.resident.count() if isinstance(b, Residential) else b.employee.count(),
                'max_employees': sum(
                    [b.elementary_employee_needed, b.college_employee_needed, b.phd_employee_needed]
                ) if isinstance(b, BuldingsWithWorkes) else 0,
                'elementary_employees': [e for e in citizens if e.workplace_object == b
                                         and self.citizens_in_city[e]['current_profession'].education == ELEMENTARY]
                if isinstance(b, BuldingsWithWorkes) else 0,
                'elementary_vacancies': b.elementary_employee_needed - len(
                    [e for e in citizens if e.workplace_object == b
                     and self.citizens_in_city[e]['current_profession'].education == ELEMENTARY]
                ) if isinstance(b, BuldingsWithWorkes) else 0,
                'college_employees': [e for e in citizens if e.workplace_object == b
                                      and self.citizens_in_city[e]['current_profession'].education == COLLEGE]
                if isinstance(b, BuldingsWithWorkes) else 0,
                'college_vacancies': b.college_employee_needed - len(
                    [e for e in citizens if e.workplace_object == b
                     and self.citizens_in_city[e]['current_profession'].education == COLLEGE]
                ) if isinstance(b, BuldingsWithWorkes) else 0,
                'phd_employees': [e for e in citizens if e.workplace_object == b
                                  and self.citizens_in_city[e]['current_profession'].education == PHD]
                if isinstance(b, BuldingsWithWorkes) else 0,
                'phd_vacancies':b.phd_employee_needed - len(
                    [e for e in citizens if e.workplace_object == b
                     and self.citizens_in_city[e]['current_profession'].education == PHD]
                ) if isinstance(b, BuldingsWithWorkes) else 0,
            }

    def preprocess_citizens(self, citizens):
        for citizen in citizens:
            self.to_save.append(citizen)
            citizen_dict = {}
            educations = citizen.education_set.all()
            professions = citizen.profession_set.all()
            self.to_save += list(educations) + list(professions)
            current_educations = [e for e in educations if e.if_current is True]
            current_professions = [p for p in professions if p.if_current is True]
            citizen_dict['educations'] = educations
            citizen_dict['professions'] = professions
            citizen_dict['current_education'] = None
            citizen_dict['current_profession'] = None
            if current_educations:
                ce = current_educations.pop()
                citizen_dict['current_education'] = ce
            if current_professions:
                cp = current_professions.pop()
                citizen_dict['current_profession'] = cp
            self.citizens_in_city[citizen] = citizen_dict

    def preprocess_vehicles(self, vehicles, citizens):
        for vehicle in vehicles:
            self.to_save.append(vehicle)
            self.vehicles[vehicle] = {
                'people_in_charge': vehicle.employee.count(),
                'max_employees': sum(
                    [vehicle.elementary_employee_needed, vehicle.college_employee_needed, vehicle.phd_employee_needed]),
                'elementary_employees': [c for c in citizens if c.workplace_object == vehicle and c.edu_title == ELEMENTARY],
                'elementary_vacancies': vehicle.elementary_employee_needed - len(
                    [c for c in citizens if c.workplace_object == vehicle
                     and self.citizens_in_city[c]['current_profession'].education == ELEMENTARY]
                ),
                'college_employees': [c for c in citizens if c.workplace_object == vehicle and c.edu_title == COLLEGE],
                'college_vacancies': vehicle.college_employee_needed - len(
                    [c for c in citizens if c.workplace_object == vehicle
                     and self.citizens_in_city[c]['current_profession'].education == COLLEGE]
                ),
                'phd_employees': [c for c in citizens if c.workplace_object == vehicle and c.edu_title == PHD],
                'phd_vacancies': vehicle.phd_employee_needed - len(
                    [c for c in citizens if c.workplace_object == vehicle
                     and self.citizens_in_city[c]['current_profession'].education == PHD]
                )
            }

    def preprocess_city_fields(self):
        for field in CityField.objects.filter(city=self.city):
            self.city_fields_in_city[field] = {'row_col': (field.row, field.col), 'pollution': field.pollution}
            self.to_save.append(field)

    def preprocess_data(self):
        citizens = Citizen.objects.filter(city=self.city)
        buildings = self.get_quersies_of_buildings()
        vehicles = self.get_queries_of_vehicles()
        self.preprocess_citizens(citizens)
        self.preprocess_buildings(buildings, citizens)
        self.preprocess_vehicles(vehicles, citizens)
        self.preprocess_city_fields()

    def datasets_for_turn_calculation(self):
        power_resources_allocation_dataset = {
            'resource': 'energy',
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings if isinstance(b, PowerPlant)},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if not isinstance(b, PowerPlant)},
            'allocated_resource': 'energy_allocated',
            'msg': 'power'
        }
        raw_water_resources_allocation_dataset = {
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings if isinstance(b, Waterworks)},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if isinstance(b, SewageWorks)},
            'allocated_resource': 'raw_water_allocated',
            'msg': 'raw_water'
        }
        clean_water_resources_allocation_dataset = {
            'list_of_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings if isinstance(b, SewageWorks)},
            'list_without_source': {b: self.list_of_buildings[b] for b in self.list_of_buildings
                                    if not isinstance(b, SewageWorks) and not isinstance(b, Waterworks)},
            'allocated_resource': 'clean_water_allocated',
            'msg': 'clean_water'
        }
        return [power_resources_allocation_dataset, raw_water_resources_allocation_dataset, clean_water_resources_allocation_dataset]


