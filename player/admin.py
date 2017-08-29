from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_filter = ['user', 'current_turn', 'email_confirmed']

admin.site.register(Profile, ProfileAdmin)
