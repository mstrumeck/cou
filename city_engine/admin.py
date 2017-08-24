from django.contrib import admin
from .models import City, TurnSystem


class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'publish', 'updated']
    list_filter = ['name', 'user', 'publish', 'updated']
    ordering = ['publish']
    date_hierarchy = 'publish'
admin.site.register(City, CityAdmin)


class TurnAdmin(admin.ModelAdmin):
    list_display = ['city', 'current_turn', 'max_turn']
admin.site.register(TurnSystem, TurnAdmin)