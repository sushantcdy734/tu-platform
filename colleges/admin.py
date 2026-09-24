from django.contrib import admin
from .models import District, College


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'province']
    search_fields = ['name', 'province']


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'district', 'status', 'created_at']
    list_filter = ['status', 'district']
    search_fields = ['name', 'code', 'email']