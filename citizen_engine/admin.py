from django.contrib import admin
from .models import Citizen


class CitizenAdmin(admin.ModelAdmin):
    list_display = ['city', 'age', 'health']
    list_filter = ['city']
admin.site.register(Citizen, CitizenAdmin)