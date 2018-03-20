import os


def run_tests():
    os.system('python manage.py test'
              ' citizen_engine'
              ' city_engine'
              ' player'
              ' functional_tests.legacy.game_tests'
              ' functional_tests.legacy.user_tests')

run_tests()
