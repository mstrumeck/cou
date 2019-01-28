from city_engine.main_view_data.global_variables import HEX_NUM_IN_ROW, ROW_NUM
from city_engine.models import PowerPlant, Waterworks, SewageWorks


class ResourceAllocation:

    def __init__(self, city, data):
        self.city = city
        self.data = data
        self.fields_in_city_by_corr = {self.data.city_fields_in_city[f].row_col: f for f in self.data.city_fields_in_city}

    def run(self):
        self.clean_allocation_data()
        self.all_resource_allocation()
        self.pollution_allocation()

    def clean_allocation_data(self):
        for f in self.data.city_fields_in_city:
            f.pollution = 0
        for b in [b for b in self.data.list_of_buildings if isinstance(b, PowerPlant)]:
            b.energy_allocated = 0
        for b in [b for b in self.data.list_of_buildings if isinstance(b, Waterworks)]:
            b.raw_water_allocated = 0
        for b in [b for b in self.data.list_of_buildings if isinstance(b, SewageWorks)]:
            b.raw_water = 0
            b.clean_water_allocated = 0
        for b in self.data.list_of_buildings:
            b.water = 0
            b.energy = 0

    def all_resource_allocation(self):
        for dataset in self.data.datasets_for_turn_calculation():
            self.resource_allocation(dataset)
        self.pollution_allocation()

    def resource_allocation(self, dataset):
        for provider_ob in dataset['list_of_source']:
            source_keys = [dataset['list_without_source'][b].row_col_cor
                           for b in dataset['list_without_source']]
            pattern = sorted(source_keys, key=lambda x: (
                abs(x[0] - dataset['list_of_source'][provider_ob].row_col_cor[0]),
                abs(x[1] - dataset['list_of_source'][provider_ob].row_col_cor[1])))
            allocated_resource = dataset['allocated_resource']
            provider_total_production = provider_ob.total_production(self.data.list_of_workplaces, self.data.citizens_in_city)
            guard = 0
            while getattr(provider_ob, allocated_resource) < provider_total_production and guard < len(dataset['list_without_source']):
                key = pattern[guard]
                provider_ob.allocate_resource_in_target(
                    next(b for b in dataset['list_without_source']
                         if dataset['list_without_source'][b].row_col_cor == key),
                    provider_total_production
                )
                guard += 1

    def pollution_allocation(self):
        for build in self.data.list_of_buildings:
            surroundings = self.field_surroundings(self.data.list_of_buildings[build].row_col_cor)
            pollution_to_allocate = build.pollution_calculation(
                self.data.list_of_buildings[build].people_in_charge
            )/len(surroundings)
            for field in [self.data.city_fields_in_city[field].row_col for field in self.data.city_fields_in_city
                          if self.data.city_fields_in_city[field].row_col in surroundings]:
                self.fields_in_city_by_corr[field].pollution += pollution_to_allocate

    def field_surroundings(self, field):
        row = field[0]
        col = field[1]
        pattern = [(row+1, col-1), (row+1, col), (row+1, col+1), (row, col-1),
                (row, col+1), (row-1, col-1), (row-1, col), (row-1, col+1)]
        return [sur for sur in pattern if
                (sur[0] >= 0 and sur[0] <= ROW_NUM) and (sur[1] >= 0 and sur[1] <= HEX_NUM_IN_ROW)]
