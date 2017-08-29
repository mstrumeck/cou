from django.contrib import admin
from .models import City, Residential


class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'publish', 'updated']
    list_filter = ['name', 'user', 'publish', 'updated']
    ordering = ['publish']
    date_hierarchy = 'publish'
admin.site.register(City, CityAdmin)


class ResidentialAdmin(admin.ModelAdmin):
    list_display = ['city', 'max_population']
admin.site.register(Residential, ResidentialAdmin)