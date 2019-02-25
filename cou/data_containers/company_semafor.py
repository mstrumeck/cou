from .base_semafor import BaseSemafor
from company_engine.models import FoodCompany, Food
from resources.models import Mass


class CompanySemafor(BaseSemafor):

    def select_semafor_schema(self, data_container, citizens, citizens_data):
        if isinstance(data_container.bi, FoodCompany):
            self._create_data_for_food_company(data_container, citizens, citizens_data)

    def _create_data_for_food_company(self, data_container, citizens, citizens_data):
        self._create_data_for_building_with_worker(data_container, citizens, citizens_data)
        data_container.available_components = [Mass]
        data_container.goods_to_product = [Food]
