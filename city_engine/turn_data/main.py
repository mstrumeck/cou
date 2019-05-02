from citizen_engine.social_actions import SocialAction
from city_engine.main_view_data.resources_allocation import ResourceAllocation
from city_engine.main_view_data.trash_management import TrashManagement, CollectGarbage
from city_engine.models import Farm, AnimalFarm
from resources.models import MassConventer


class TurnCalculation:
    def __init__(self, city, data, profile):
        self.city = city
        self.data = data
        self.profile = profile

    def run(self):
        TrashManagement(self.data).run()
        SocialAction(self.city, self.profile, self.data).run()
        ResourceAllocation(self.city, self.data).run()
        CollectGarbage(self.city, self.data).run()
        self.financial_actions()
        self.collect_mass()
        self.execute_maintenance()
        self.update_build_status()
        self.update_harvest_status()
        self.update_breeding_status()
        self.trade_district_actions()
        self.save_all()

    def save_all(self):
        self.city.save()
        self.data.market.save_all()
        for instance in self.data.to_save:
            instance.save()
        for company in self.data.companies:
            self.data.companies[company].save_all()
        self.profile.current_turn += 1
        self.profile.save()

    def financial_actions(self):
        for f in self.data.families:
            self.data.families[f].pay_rent(self.city, self.profile)

    def trade_district_actions(self):
        for c in self.data.companies:
            self.data.list_of_buildings[c].create_goods()

    def collect_mass(self):
        for mass_collector in [
            mc for mc in self.data.list_of_buildings if isinstance(mc, MassConventer)
        ]:
            mass_collector.product_mass(self.data)

    def update_breeding_status(self):
        for farm in [
            b for b in self.data.list_of_buildings if isinstance(b, AnimalFarm)
        ]:
            farm.farm_operation(self.data)
            if self.data.list_of_buildings[farm].cattle:
                self.data.to_save.append(self.data.list_of_buildings[farm].cattle)

    def update_harvest_status(self):
        for farm in [b for b in self.data.list_of_buildings if isinstance(b, Farm)]:
            farm.update_harvest(self.profile.current_turn, self.data)

    def update_build_status(self):
        for building in self.data.list_of_buildings:
            if building.if_under_construction is True:
                building.build_status()

    def calculate_maintenance_cost(self):
        return sum([b.maintenance_cost for b in self.data.list_of_buildings])

    def execute_maintenance(self):
        self.city.cash - self.calculate_maintenance_cost()
