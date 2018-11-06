from cou.global_var import ELEMENTARY, COLLEGE, PHD


class CitizenWorkEngine:
    def __init__(self, city_data):
        self.data = city_data

    def human_resources_allocation(self):
        self.assign_better_job()
        self.assign_job_for_people_without_it()

    def assign_better_job(self):
        matrix = {ELEMENTARY: 'elementary_vacancies', COLLEGE: 'college_vacancies', PHD: 'phd_vacancies', 'None': 'elementary_vacancies'}
        for e in (u for u in self.data.citizens_in_city
                  if u.workplace_object is not None
                  and self.data.citizens_in_city[u]['current_profession'].education != u.edu_title
                  and [x for x in self.data.list_of_workplaces if self.data.list_of_workplaces[x][matrix[u.edu_title]]]):
            e.change_work_for_better(self.data.list_of_workplaces, self.data.citizens_in_city, self.data.to_save)

    def assign_job_for_people_without_it(self):
        for e in (u for u in self.data.citizens_in_city
                  if u.workplace_object is None
                     and u.resident_object is not None
                     and u.age >= 18):
            e.find_work(self.data.list_of_workplaces, self.data.citizens_in_city, self.data.to_save)