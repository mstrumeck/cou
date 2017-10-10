from city_engine.models import list_of_models
from django.db.models import Sum


def update_build_status(city):
    for model in list_of_models:
        for building in model.objects.filter(city=city):
            building.build_status()
    city.save()


def calculate_maintenance_cost(list_of_models, city):
    maintenance_cost = 0
    for model in list_of_models:
        total_cost_per_model = model.objects.aggregate(Sum('maintenance_cost'))['maintenance_cost__sum']
        if total_cost_per_model is not None:
            maintenance_cost += total_cost_per_model
    city.cash -= maintenance_cost
    city.save()



