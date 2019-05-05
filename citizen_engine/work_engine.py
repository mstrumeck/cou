from citizen_engine.models import Education
from city_engine.models import ProductionBuilding
from company_engine.models import Company


class CitizenWorkEngine:
    def __init__(self, city_data, city):
        self.data = city_data
        self.city = city
        self.active_workplaces = {
            w: self.data.list_of_workplaces[w]
            for w in self.data.list_of_workplaces
            if isinstance(w, Company)
            or w.if_under_construction is False
        }

    def human_resources_allocation(self):
        self.update_work_experience()
        if self.active_workplaces:
            self.assign_better_job()
            self.assign_job_for_people_without_it()
            self.assign_job_for_people_without_education()
            self.wage_payment_in_all_workplaces()

    def update_work_experience(self):
        for wb in self.data.list_of_workplaces:
            self.data.list_of_workplaces[wb].update_proficiency_of_profession_for_employees()

    def assign_better_job(self):
        for e in (
            u
            for u in self.data.citizens_in_city
            if u.workplace_object is not None
            and self.data.citizens_in_city[u].current_profession.education
            != u.edu_title
        ):
            if [
                b
                for b in self.data.list_of_workplaces
                if getattr(
                    self.data.list_of_workplaces[b], Education.MATRIX[e.edu_title]
                )
            ]:
                e.change_work_for_better(
                    self.active_workplaces,
                    self.data.citizens_in_city,
                    self.data.to_save,
                )

    def assign_job_for_people_without_it(self):
        for e in (
            u
            for u in self.data.citizens_in_city
            if u.workplace_object is None
            and u.resident_object is not None
            and u.age >= 18
            and u.edu_title != "None"
        ):
            e.find_work(
                self.active_workplaces, self.data.citizens_in_city, self.data.to_save
            )

    def assign_job_for_people_without_education(self):
        if [
            w
            for w in self.active_workplaces
            if self.active_workplaces[w].elementary_vacancies
        ]:
            workplaces_without_qualifications = [
                w
                for w in self.active_workplaces
                if self.active_workplaces[w].elementary_vacancies
            ]
            for e in (
                u
                for u in self.data.citizens_in_city
                if u.workplace_object is None
                and u.resident_object is not None
                and u.age >= 18
                and u.edu_title == "None"
            ):
                e.grab_job(
                    workplaces_without_qualifications,
                    self.active_workplaces,
                    e.edu_title,
                    self.data.citizens_in_city,
                    self.data.to_save,
                )

    def wage_payment_in_all_workplaces(self):
        for w in (self.data.list_of_workplaces[w] for w in self.data.list_of_workplaces
                  if not isinstance(w, Company) or not isinstance(w, ProductionBuilding)
                  ):
            w.wage_payment(self.city)
