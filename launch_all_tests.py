import os


def run_tests():
    os.system('python manage.py test'
              ' citizen_engine'
              ' city_engine'
              ' player'
              ' functional_tests.legacy.game_tests'
              ' functional_tests.legacy.user_tests'
              ' functional_tests.trashcollector_tests')


def run_tests_with_coverage():
    os.system("coverage run --source='.' manage.py test citizen_engine \
                                         city_engine \
                                         player \
                                         functional_tests.legacy.game_tests \
                                         functional_tests.legacy.user_tests \
                                         functional_tests.trashcollector_tests \
                                         functional_tests.resource_allocation_tests")

# run_tests_with_coverage()
run_tests()