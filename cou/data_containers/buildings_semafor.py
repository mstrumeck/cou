from django.apps import apps

from city_engine.models import Waterworks, WindPlant, PowerPlant, \
    DustCart, SewageWorks, BuldingsWithWorkes, \
    DumpingGround, TradeDistrict, CoalPlant, RopePlant, Building, Farm
from company_engine.models import Company
from resources.models import AnimalFarm, Cattle
from .base_semafor import BaseSemafor
from .data_containers import VehicleDataContainer


class BuildingSemafor(BaseSemafor):

    def select_semafor_schema(self, data_container, citizens, citizens_data, vehicles):
        if isinstance(data_container.bi, Building):
            data_container.water_required = 10
            data_container.energy_required = 10
        if isinstance(data_container.bi, BuldingsWithWorkes):
            self._create_data_for_building_with_worker(data_container, citizens, citizens_data)
            data_container.productivity = data_container._get_productivity(citizens_data)
        if isinstance(data_container.bi, AnimalFarm):
            self._create_data_for_animal_farm(data_container)
        if isinstance(data_container.bi, TradeDistrict):
            self._create_data_for_trade_district(data_container)
        if isinstance(data_container.bi, DumpingGround):
            self._create_data_for_dumping_ground(
                data_container, citizens, citizens_data, vehicles)
        if isinstance(data_container.bi, PowerPlant):
            self._create_powerplant_schema(data_container, citizens_data)
        if isinstance(data_container.bi, Waterworks):
            self._create_waterworks_schema(data_container, citizens_data)
        if isinstance(data_container.bi, SewageWorks):
            self._create_sewageworks_schema(data_container, citizens_data)

    def _create_data_for_dumping_ground(self, data_container, citizens, citizens_in_city, vehicles):
        if DustCart.objects.filter(dumping_ground=data_container.bi).exists:
            for dc in DustCart.objects.filter(dumping_ground=data_container.bi):
                vdc = VehicleDataContainer(
                    instance=dc
                )
                self._create_data_for_building_with_worker(vdc, citizens, citizens_in_city)
                vehicles[dc] = vdc

    def _create_data_for_animal_farm(self, data_container):
        cattle_query = Cattle.objects.filter(farm=data_container.bi)
        if cattle_query:
            data_container.cattle = list(cattle_query).pop()
        else:
            data_container.cattle = []

    def _create_sewageworks_schema(self, data_container, citizens_data):
            data_container.raw_water_required = 1000
            data_container.clean_water_allocated = 0
            data_container.total_production = data_container._get_clean_water_total_production(citizens_data)

    def _create_waterworks_schema(self, data_container, citizens_data):
            data_container.raw_water_production = 100
            data_container.raw_water_allocated = 0
            data_container.total_production = self._get_water_tower_total_production(data_container, citizens_data)

    def _create_powerplant_schema(self, data_container, citizens_data):
        if isinstance(data_container.bi, WindPlant):
            data_container.energy_production = 100
            data_container.max_power_nodes = 10
            data_container.water_required = 20
        if isinstance(data_container.bi, CoalPlant):
            data_container.energy_production = 200
            data_container.max_power_nodes = 2
            data_container.water_required = 20
        if isinstance(data_container.bi, RopePlant):
            data_container.energy_production = 150
            data_container.max_power_nodes = 4
            data_container.water_required = 20
        data_container.energy_allocated = 0
        data_container.energy_required = 0
        data_container.total_production = self._get_power_plant_total_production(data_container, citizens_data)

    def _create_data_for_trade_district(self, data_container):
        data_container.people_in_charge = 0
        for model in [
            model
            for model in apps.get_app_config("company_engine").get_models()
            if issubclass(model, Company) and model is not Company
        ]:
            if model.objects.filter(trade_district=data_container.bi).exists():
                for instance in model.objects.filter(trade_district=data_container.bi):
                    data_container.people_in_charge += instance.employee.count()

    def _get_water_tower_total_production(self, data_container, citizens_data):
        if data_container.employee_productivity(citizens_data) == 0:
            return 0
        else:
            t = [
                data_container.employee_productivity(citizens_data),
                data_container._energy_productivity(),
            ]
            return int(float(sum(t)) / float(len(t)) * data_container.raw_water_production)

    def _get_power_plant_total_production(self, data_container, citizens_data):
        if data_container.employee_productivity(citizens_data) == 0:
            return 0
        else:
            t = [
                data_container.employee_productivity(citizens_data),
                data_container._water_productivity(),
            ]
            return int(
                (float(sum(t)) / float(len(t)))
                * data_container.energy_production
                * data_container.bi.power_nodes
            )
