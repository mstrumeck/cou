import os


def run_tests():
    os.system('python manage.py test'
              ' citizen_engine'
              ' city_engine'
              ' player'
              ' resources'
              ' functional_tests.legacy.game_tests'
              ' functional_tests.legacy.user_tests'
              ' functional_tests.trashcollector_tests'
              ' functional_tests.resource_allocation_tests'
              ' functional_tests.resources_view_tests'
              ' functional_tests.mass_productions_tests'
              ' functional_tests.trade_district_tests'
              ' functional_tests.citizen_tests'
              ' functional_tests.education_tests'
              ' functional_tests.gain_experience_tests')


def run_tests_with_coverage():
    os.system("coverage run --source='.' manage.py test \
                                         citizen_engine \
                                         city_engine \
                                         player \
                                         functional_tests.legacy.game_tests \
                                         functional_tests.legacy.user_tests \
                                         functional_tests.trashcollector_tests \
                                         functional_tests.resource_allocation_tests")

# run_tests_with_coverage()
run_tests()

# python manage.py dumpdata citizen_engine city_engine auth.user --indent=2 --output=city_engine/fixtures/fixture_natural_resources.json
