

class CitizenWorkEngine:
    def __init__(self, citizens_in_city, workplaces_in_city):
        self.citizens_in_city = citizens_in_city
        self.workplaces_in_city = workplaces_in_city

    def human_resources_allocation(self):
        unemployees = (u for u in self.citizens_in_city
                             if u.workplace_object is None
                             and u.resident_object is not None
                             and u.age >= 18)
        for e in unemployees:
            e.find_work(self.workplaces_in_city, self.citizens_in_city)