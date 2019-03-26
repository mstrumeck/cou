from django.contrib import admin


class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "publish", "updated"]
    list_filter = ["publish", "updated"]
    ordering = ["publish"]
    date_hierarchy = "publish"
