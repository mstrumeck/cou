from city_engine.models import PowerPlant, ProductionBuilding, Residential


def update_turn_status(city):
    models = [PowerPlant, ProductionBuilding, Residential]
    for model in models:
        for building in model.objects.filter(city=city):
            building.build_status()

