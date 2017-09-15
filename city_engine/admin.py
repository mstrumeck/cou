from django.contrib import admin
from .models import City, Residential, ProductionBuilding, CityField


class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'publish', 'updated']
    list_filter = ['publish', 'updated']
    ordering = ['publish']
    date_hierarchy = 'publish'
admin.site.register(City, CityAdmin)


class ResidentialAdmin(admin.ModelAdmin):
    list_display = ['city_field', 'max_population']
admin.site.register(Residential, ResidentialAdmin)


class ProductionAdmin(admin.ModelAdmin):
    list_display = ['city_field', 'current_employees']
admin.site.register(ProductionBuilding, ProductionAdmin)


class CityFieldAdmin(admin.ModelAdmin):
    list_display = ['city', 'city_id']
admin.site.register(CityField, CityFieldAdmin)