from city_engine.models import list_of_models


def update_turn_status(city):
    for model in list_of_models:
        for building in model.objects.filter(city=city):
            building.build_status()

