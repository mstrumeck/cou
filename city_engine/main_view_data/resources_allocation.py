from city_engine.models import CityField
from django.db.models import F
from city_engine.main_view_data.global_variables import HEX_NUM_IN_ROW, ROW_NUM


class ResourceAllocation(object):

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def run(self):
        self.clean_city_field_data()
        self.all_resource_allocation()
        self.pollution_allocation()

    def clean_city_field_data(self):
        CityField.objects.filter(city=self.city).update(pollution=0)

    def all_resource_allocation(self):
        for dataset in self.data.datasets_for_turn_calculation():
            self.resource_allocation(dataset)
        self.pollution_allocation()

    def resource_allocation(self, dataset):
        for provider_ob in dataset['list_of_source']:
            source_keys = list(dataset['list_without_source'].keys())
            pattern = sorted(source_keys, key=lambda x: (abs(x[0] - provider_ob.city_field.row),
                                                         abs(x[1] - provider_ob.city_field.col)))
            allocated_resource = dataset['allocated_resource']
            provider_total_production = provider_ob.total_production()
            guard = 0
            while getattr(provider_ob, allocated_resource) < provider_total_production and guard < len(dataset['list_without_source']):
                key = pattern[guard]
                provider_ob.allocate_resource_in_target(dataset['list_without_source'][key], provider_total_production)
                guard += 1

    # def pollution_allocation(self):
    #     build = {b.city_field: b for b in self.data.list_of_buildings}
    #     for field in CityField.objects.filter(city=self.city):
    #         if field in build:
    #             target_build = build[field]
    #             pattern = AllocationPattern().return_first_allocation(field.row, field.col) #DOKONCZ
    #             for corr in pattern:
    #                 if CityField.objects.filter(city=self.city, row=corr[0], col=corr[1]).exists():
    #                     target_city_field = CityField.objects.get(city=self.city, row=corr[0], col=corr[1])
    #                     target_city_field.pollution += (target_build.pollution_calculation() / len(pattern))
    #                     field.pollution = F('pollution') + (target_build.pollution_calculation() / len(pattern))
    #                     target_city_field.save()
    #                     target_city_field.refresh_from_db()

    def pollution_allocation(self):
        builds = {b.city_field: b for b in self.data.list_of_buildings}
        fields = {(field.row, field.col): field for field in CityField.objects.filter(city=self.city)}
        for field in builds.keys():
            surroundings = self.field_surroundings(field)
            pollution_to_alocate = builds[field].pollution_calculation()/len(surroundings)
            for sur in surroundings:
                try:
                    target = fields[sur]
                    target.pollution = F('pollution') + pollution_to_alocate
                    target.save()
                except(KeyError):
                    continue

    def field_surroundings(self, field):
        row = field.row
        col = field.col
        pattern = [(row+1, col-1), (row+1, col), (row+1, col+1), (row, col-1),
                (row, col+1), (row-1, col-1), (row-1, col), (row-1, col+1)]
        return [sur for sur in pattern if
                (sur[0] >= 0 and sur[0] <= ROW_NUM) and (sur[1] >= 0 and sur[1] <= HEX_NUM_IN_ROW)]
