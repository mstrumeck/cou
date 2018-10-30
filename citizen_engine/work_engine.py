

class CitizenWorkEngine:
    def __init__(self, city_data):
        self.data = city_data

    def human_resources_allocation(self):
        for e in (u for u in self.data.citizens_in_city
                  if u.workplace_object is None
                     and u.resident_object is not None
                     and u.age >= 18):
            e.find_work(self.data.list_of_workplaces, self.data.citizens_in_city, self.data.to_save)