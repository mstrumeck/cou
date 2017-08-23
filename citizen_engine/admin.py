from django.contrib import admin
from .models import Citizen


class CitizenAdmin(admin.ModelAdmin):
    list_display = ['name', 'surname', 'city', 'age', 'health']
    list_filter = ['name', 'city']
admin.site.register(Citizen, CitizenAdmin)