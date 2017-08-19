import os

print("Citizen engine tests.....")
os.system('python manage.py test citizen_engine')
print("City engine tests.....")
os.system('python manage.py test city_engine')
print("Login tests.....")
os.system('python manage.py test login')
