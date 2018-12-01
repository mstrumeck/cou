from cou.global_var import ELEMENTARY, COLLEGE, PHD
from city_engine.models import TradeDistrict, ProductionBuilding


class CitizenWorkEngine:
    def __init__(self, city_data, city):
        self.data = city_data
        self.city = city

    def human_resources_allocation(self):
        self.assign_better_job()
        self.assign_job_for_people_without_it()
        self.wage_payment_in_all_workplaces()

    def assign_better_job(self):
        matrix = {ELEMENTARY: 'elementary_vacancies', COLLEGE: 'college_vacancies', PHD: 'phd_vacancies', 'None': 'elementary_vacancies'}
        for e in (u for u in self.data.citizens_in_city
                  if u.workplace_object is not None
                  and self.data.citizens_in_city[u].current_profession.education != u.edu_title
                  and [x for x in self.data.list_of_workplaces if getattr(self.data.list_of_workplaces[x], matrix[u.edu_title])]):
            e.change_work_for_better(self.data.list_of_workplaces, self.data.citizens_in_city, self.data.to_save)

    def assign_job_for_people_without_it(self):
        for e in (u for u in self.data.citizens_in_city
                  if u.workplace_object is None
                     and u.resident_object is not None
                     and u.age >= 18):
            e.find_work(self.data.list_of_workplaces, self.data.citizens_in_city, self.data.to_save)

    def wage_payment_in_all_workplaces(self):
        for w in (w for w in self.data.list_of_workplaces
                  if not isinstance(w, TradeDistrict) or
                     not isinstance(w, ProductionBuilding)):
            w.wage_payment(self.city, (self.data.citizens_in_city[e] for e in self.data.citizens_in_city if e.workplace_object == w))
