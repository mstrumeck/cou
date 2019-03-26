from city_engine.main_view_data.global_variables import HEX_NUM_IN_ROW, ROW_NUM
from city_engine.models import PowerPlant, Waterworks, SewageWorks


class ResourceAllocation:
    def __init__(self, city, data):
        self.city = city
        self.data = data
        self.fields_in_city_by_corr = {
            self.data.city_fields_in_city[f].row_col: f
            for f in self.data.city_fields_in_city
        }

    def run(self):
        # self.clean_allocation_data()
        self.all_resource_allocation()
        # self.pollution_allocation()

    def clean_allocation_data(self):
        for f in self.data.city_fields_in_city:
            f.pollution = 0

    def all_resource_allocation(self):
        for dataset in self.data.datasets_for_turn_calculation():
            self.resource_allocation(dataset)
        self.pollution_allocation()

    def resource_allocation(self, dataset):
        for provider_ob in dataset["list_of_source"]:
            second_pattern = sorted([(b.row_col_cor, b) for b in dataset["list_without_source"]], key=lambda x: (
                    abs(x[0][0] - provider_ob.row_col_cor[0]),
                    abs(x[0][1] - provider_ob.row_col_cor[1]),
                ))
            allocated_resource = dataset["allocated_resource"]
            provider_total_production = provider_ob.total_production
            guard = 0
            while getattr(provider_ob, allocated_resource) < provider_total_production \
                    and guard < len(second_pattern):
                provider_ob.allocate_resources_in_target(
                    second_pattern[guard][1],
                    self.data
                )
                guard += 1

    def pollution_allocation(self):
        for build in self.data.list_of_buildings:
            surroundings = self.field_surroundings(
                self.data.list_of_buildings[build].row_col_cor
            )
            pollution_to_allocate = self.get_pollution_to_allocate(build, surroundings)
            if pollution_to_allocate:
                for field in [
                    self.data.city_fields_in_city[field].row_col
                    for field in self.data.city_fields_in_city
                    if self.data.city_fields_in_city[field].row_col in surroundings
                ]:
                    self.fields_in_city_by_corr[field].pollution += pollution_to_allocate

    def get_pollution_to_allocate(self, build, surroundings):
        pollution_in_build = build.pollution_calculation(self.data.list_of_buildings[build].people_in_charge)
        if pollution_in_build and surroundings:
            return pollution_in_build / len(surroundings)
        return 0

    def field_surroundings(self, field):
        row = field[0]
        col = field[1]
        pattern = [
            (row + 1, col - 1),
            (row + 1, col),
            (row + 1, col + 1),
            (row, col - 1),
            (row, col + 1),
            (row - 1, col - 1),
            (row - 1, col),
            (row - 1, col + 1),
        ]
        return [
            sur
            for sur in pattern
            if (sur[0] >= self.data.min_row and sur[0] <= self.data.max_row)
            and (sur[1] >= self.data.min_col and sur[1] <= self.data.max_col)
        ]
