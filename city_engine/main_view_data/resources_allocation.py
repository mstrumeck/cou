from city_engine.main_view_data.allocation_pattern import AllocationPattern
from city_engine.models import CityField, PowerPlant, Waterworks, WindPlant, WaterTower
from city_engine.main_view_data.trash_management import CollectGarbage
from city_engine.abstract import RootClass
from django.db.models import F


class ResourceAllocation(object):

    def __init__(self, city, data):
        self.city = city
        self.data = data

    def run(self):
        self.clean_city_field_data()
        self.all_resource_allocation()
        self.pollution_allocation()
        CollectGarbage(self.city, self.data).run()

    def clean_city_field_data(self):
        CityField.objects.filter(city=self.city).update(pollution=0)

    def all_resource_allocation(self):
        for dataset in self.data.datasets_for_turn_calculation():
            self.resource_allocation(dataset)
        self.pollution_allocation()

    def if_building_exist(self, field, dataset):
        if field in dataset['list_without_source']:
            return dataset['list_without_source'][field]

    def update_attr(self, ob, val_to_up, val):
        setattr(ob, val_to_up, getattr(ob, val_to_up) + val)

    def resource_allocation(self, dataset):
        for provider_ob in dataset['list_of_source']:
            resource_required = dataset['resource_required']
            resource = dataset['resource']
            allocated_resource = dataset['allocated_resource']
            pattern = AllocationPattern().create_allocation_pattern(provider_ob.city_field.row, provider_ob.city_field.col)
            provider_total_production = provider_ob.total_production()
            if getattr(provider_ob, allocated_resource) < provider_total_production:
                while getattr(provider_ob, allocated_resource) < provider_total_production:
                    try:
                        next_corrs = next(pattern)
                    except(StopIteration):
                        break
                    for field in next_corrs:
                        if self.if_building_exist(field, dataset):
                            target_ob = self.if_building_exist(field, dataset)
                            resource_left = provider_total_production - getattr(provider_ob, allocated_resource)
                            resource_to_fill = getattr(target_ob, resource_required) - getattr(target_ob,resource)
                            if resource_left >= resource_to_fill:
                                self.update_attr(provider_ob, allocated_resource, resource_to_fill)
                                self.update_attr(target_ob, resource, resource_to_fill)
                            elif resource_left < resource_to_fill:
                                self.update_attr(provider_ob, allocated_resource, resource_left)
                                self.update_attr(target_ob, resource, resource_left)
                            provider_ob.save()
                            target_ob.save()

    def pollution_allocation(self):
        build = {(b.city_field): b for b in self.data.list_of_buildings}
        for field in CityField.objects.filter(city=self.city):
            if field in build:
                target_build = build[field]
                allocation_pattern = AllocationPattern().return_first_allocation(field.row, field.col)
                for corr in allocation_pattern:
                    if CityField.objects.filter(city=self.city, row=corr[0], col=corr[1]).exists():
                        target_city_field = CityField.objects.get(city=self.city, row=corr[0], col=corr[1])
                        target_city_field.pollution += (target_build.pollution_calculation() / len(allocation_pattern))
                        field.pollution = F('pollution') + (target_build.pollution_calculation() / len(allocation_pattern))
                        target_city_field.save()
